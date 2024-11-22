import torch
import torch.nn as nn
import torch.optim as optim

device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")


# Define Kernel function
def kernel(u, v):
    """
    Sparsifying kernel function

    :param u: input vectors [n_in, 1, n_dim]
    :param v: output vectors [1, n_hid, n_dim]
    :return: input to output connection matrix
    """
    dist = torch.norm(u - v, p=2, dim=2)
    hat = torch.clamp(1.0 - dist**2, min=0.0)
    return hat


# Kernel Layer
class KernelLayer(nn.Module):
    def __init__(
        self,
        n_in,
        n_hid=500,
        n_dim=5,
        activation=torch.sigmoid,
        lambda_s=0.01,
        lambda_2=0.01,
    ):
        super().__init__()
        self.n_hid = n_hid
        self.n_dim = n_dim
        self.activation = activation
        self.lambda_s = lambda_s
        self.lambda_2 = lambda_2

        # Initialize weights
        self.W = nn.Parameter(torch.randn(n_in, n_hid) * 0.01)
        self.u = nn.Parameter(torch.randn(n_in, 1, n_dim) * 1e-3)
        self.v = nn.Parameter(torch.randn(1, n_hid, n_dim) * 1e-3)
        self.b = nn.Parameter(torch.zeros(n_hid))

    def forward(self, x):
        # Compute the sparsifying kernel
        w_hat = kernel(self.u, self.v)

        # Regularization terms
        sparse_reg_term = self.lambda_s * torch.sum(w_hat**2)
        l2_reg_term = self.lambda_2 * torch.sum(self.W**2)

        # Compute effective weights
        W_eff = self.W * w_hat

        # Compute output
        y = torch.matmul(x, W_eff) + self.b
        y = self.activation(y)
        return y, sparse_reg_term + l2_reg_term


# Full Model
class KernelNetwork(nn.Module):
    def __init__(self, n_u, n_layers, n_hid=500, n_dim=5, lambda_s=0.01, lambda_2=0.01):
        super().__init__()
        self.n_layers = n_layers
        self.layers = nn.ModuleList()

        for i in range(n_layers):
            self.layers.append(
                KernelLayer(
                    n_u if i == 0 else n_hid,
                    n_hid,
                    n_dim,
                    lambda_s=lambda_s,
                    lambda_2=lambda_2,
                )
            )

        self.output_layer = KernelLayer(
            n_hid, n_u, activation=lambda x: x, lambda_s=lambda_s, lambda_2=lambda_2
        )

    def forward(self, x):
        reg_loss = 0
        for i, layer in enumerate(self.layers):
            x, reg = layer(x)
            reg_loss += reg

        prediction, reg = self.output_layer(x)
        reg_loss += reg
        return prediction, reg_loss


class Loss(nn.Module):
    def forward(self, pred_p, reg_loss, train_m, train_r):
        # L2 loss
        diff = train_m * (train_r - pred_p)
        sqE = torch.nn.functional.mse_loss(
            diff, torch.zeros_like(diff), reduction="sum"
        )
        loss_p = sqE + reg_loss
        return loss_p


class Rating:

    def __init__(self, n_u, n_layers, output_every, n_hid, lambda_s, lambda_2):
        self.model = KernelNetwork(
            n_u, n_layers, n_hid=n_hid, lambda_s=lambda_s, lambda_2=lambda_2
        ).to(device)
        self.optimizer = optim.LBFGS(
            self.model.parameters(), max_iter=output_every, history_size=10
        )
        self.output_every = output_every

    def train_and_validate(self, n_epoch, tr, vr, vm, tm):
        tr = tr.float().to(device)
        vr = vr.float().to(device)
        vm = vm.float().to(device)
        tm = tm.float().to(device)

        def closure():
            self.optimizer.zero_grad()
            x = tr
            m = tm
            self.model.train()
            prediction, reg_loss = self.model(x)
            loss = Loss().to(device)(prediction, reg_loss, m, x)
            loss.backward()
            return loss

        # Training loop
        for epoch in range(int(n_epoch / self.output_every)):
            self.optimizer.step(closure)

            with torch.no_grad():
                prediction = self.model(tr)[0]

                prediction = prediction.clone().detach()
                prediction_clipped = torch.clamp(prediction, min=1.0, max=2.0)

                error = torch.sqrt(
                    ((vm * (prediction_clipped - vr) ** 2).sum()) / vm.sum()
                )
                error_train = torch.sqrt(
                    ((tm * (prediction_clipped - tr) ** 2).sum()) / tm.sum()
                )
                print(".-^-._" * 12)
                print(
                    f"Epoch: {epoch}, Validation RMSE: {error.item():.4f}, Train RMSE: {error_train.item():.4f}"
                )
                print(".-^-._" * 12)

    def predict(self, test):
        with torch.no_grad():
            prediction = self.model(test.float().to(device))[0]
            prediction = prediction.clone().detach()
            prediction_clipped = torch.clamp(prediction, min=1.0, max=2.0)
        return prediction_clipped
