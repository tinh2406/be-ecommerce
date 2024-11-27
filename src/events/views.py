from django_eventstream.viewsets import EventsViewSet


class ChatEventsViewSet(EventsViewSet):

    def list(self, request):
        user = request.user
        self.channels = [f"user-{user.id}"]
        return super().list(request)
