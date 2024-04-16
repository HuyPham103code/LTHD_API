from rest_framework import pagination

class CoursePaginatior(pagination.PageNumberPagination):
    page_size = 5

class CommentPaginator(pagination.PageNumberPagination):
    page_size = 3

