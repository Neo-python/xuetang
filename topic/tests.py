from django.test import TestCase


# Create your tests here.
def get_page(page, page_list):
    left = 2
    right = 3
    m = page_list[-1]
    for i in range(1, 3):
        if page + i > m:
            right -= 1
            left += 1
        elif page - i < 1:
            left -= 1
            right += 1
    return list(page_list[page - left:page + right])

