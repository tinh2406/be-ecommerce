class NavigateCommand:

    GO_TO_HOME = "go_to_home"
    GO_TO_PRODUCT_DETAILS = "go_to_product_details"
    GO_TO_PROFILE = "go_to_profile"
    GO_TO_SETTINGS = "go_to_settings"
    GO_TO_LOGOUT = "go_to_logout"

    # Account & Personalization
    GO_TO_NOTIFICATION_SETTINGS = "go_to_notification_settings"
    GO_TO_PASSWORD_SETTINGS = "go_to_password_settings"
    GO_TO_PRIVACY_SETTINGS = "go_to_privacy_settings"
    GO_TO_LANGUAGE_SETTINGS = "go_to_language_settings"

    # Shopping & Orders
    GO_TO_CART = "go_to_cart"
    GO_TO_WISHLIST = "go_to_wishlist"
    GO_TO_ORDER_HISTORY = "go_to_order_history"
    GO_TO_TRACK_ORDER = "go_to_track_order"

    LIST_COMMANDS = [
        GO_TO_HOME,
        GO_TO_PRODUCT_DETAILS,
        GO_TO_PROFILE,
        GO_TO_SETTINGS,
        GO_TO_LOGOUT,
        GO_TO_NOTIFICATION_SETTINGS,
        GO_TO_PASSWORD_SETTINGS,
        GO_TO_PRIVACY_SETTINGS,
        GO_TO_LANGUAGE_SETTINGS,
        GO_TO_CART,
        GO_TO_WISHLIST,
        GO_TO_ORDER_HISTORY,
        GO_TO_TRACK_ORDER,
    ]

    NAVIGATE_ADDRESSES = {
        GO_TO_HOME: "GO_TO_HOME",
        GO_TO_PRODUCT_DETAILS: "GO_TO_PRODUCT_DETAILS",
        GO_TO_PROFILE: "GO_TO_PROFILE",
        GO_TO_SETTINGS: "GO_TO_SETTINGS",
        GO_TO_LOGOUT: "GO_TO_LOGOUT",
        GO_TO_NOTIFICATION_SETTINGS: "GO_TO_NOTIFICATION_SETTINGS",
        GO_TO_PASSWORD_SETTINGS: "GO_TO_PASSWORD_SETTINGS",
        GO_TO_PRIVACY_SETTINGS: "GO_TO_PRIVACY_SETTINGS",
        GO_TO_LANGUAGE_SETTINGS: "GO_TO_LANGUAGE_SETTINGS",
        GO_TO_CART: "GO_TO_CART",
        GO_TO_WISHLIST: "GO_TO_WISHLIST",
        GO_TO_ORDER_HISTORY: "GO_TO_ORDER_HISTORY",
        GO_TO_TRACK_ORDER: "GO_TO_TRACK_ORDER",
    }
