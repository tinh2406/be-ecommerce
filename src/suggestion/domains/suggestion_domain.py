from suggestion.services import SuggestionsService


class SuggestionDomain:
    @classmethod
    def get_suggestion(
        cls,
        user_id: str | None = None,
        latest_ratings: list | None = None,
        product_id: str | None = None,
    ):
        if user_id:
            products = SuggestionsService.get_suggestion(user_id, product_id=product_id)
        else:
            products = SuggestionsService.get_suggestion(
                latest_ratings=latest_ratings, product_id=product_id
            )
        return products
