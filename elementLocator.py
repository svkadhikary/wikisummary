

class Locator:
    def __init__(self):
        pass

    def search_input_area(self):
        area = '/html/body/div[5]/div[1]/div[2]/div/div/form/div/input[1]'
        return area

    def search_button(self):
        button = '/html/body/div[5]/div[1]/div[2]/div/div/form/div/input[3]'
        return button

    def p_element_locator(self):
        p_ele = 'p'
        return p_ele

    def img_element_locator(self):
        img_ele = 'img'
        return img_ele

    def firstHeadingLocator(self):
        f_hd = 'firstHeading'
        return f_hd

    def references_locator(self):
        r_elements = 'reference-text'
        return r_elements
