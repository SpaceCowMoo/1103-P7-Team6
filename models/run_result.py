from models.listing import Listing


class RunResult:
    """One ranked job in a run. rank 1 is the best match"""

    def __init__(self, rank: int, score: float, listing: Listing):
        self.__rank = rank
        self.__score = score
        self.__listing = listing

    def get_rank(self):
        return self.__rank

    def get_score(self):
        return self.__score

    def get_listing(self):
        return self.__listing

    def fetch_run_result_details(self):
        return {
            "rank": self.__rank,
            "score": self.__score,
            "listing": self.__listing.fetch_listing_details(),
        }
