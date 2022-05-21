from django.core.paginator import Paginator


def paginator(posts, NUMBER_OF_POSTS, page_number):
    paginator_obj = Paginator(posts, NUMBER_OF_POSTS)
    return paginator_obj.get_page(page_number)
