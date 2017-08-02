class PaginatorError(Exception):
    def __init__(self, url):
        self.url = url


class Paginator:
    def __init__(self, request, per_page):
        self.per_page = per_page
        self.query_dict = request.GET.copy()
        self.path = request.path
        self.count = None
        self.pages_total = None
        self.prev_link = None
        self.next_link = None
        try:
            pages = self.query_dict.pop('page', [])
            page = 1 if not pages else int(pages[0]) if len(pages) == 1 else 0
        except (ValueError, IndexError):
            page = 0
        if page <= 0:
            raise PaginatorError(self.to_link(1))
        self.page = page

    def set_count(self, count):
        self.count = count
        self.pages_total = (self.count + self.per_page - 1) // self.per_page
        if self.page > self.pages_total:
            raise PaginatorError(self.to_link(self.pages_total))
        self.prev_link = self.page > 1 and self.to_link(self.page - 1)
        self.next_link = self.page < self.pages_total and self.to_link(self.page + 1)

    def to_link(self, page):
        query_dict = self.query_dict
        if page != 1:
            query_dict = query_dict.copy()
            query_dict['page'] = page
        path = self.path
        return path + '?' + query_dict.urlencode() if query_dict else path


class QuerySetPaginator(Paginator):
    def __init__(self, request, query_set, per_page):
        super().__init__(request, per_page)
        self.set_count(query_set.count())
        offset = per_page * (self.page - 1)
        self.items = query_set[offset:(offset + per_page - 1)]
