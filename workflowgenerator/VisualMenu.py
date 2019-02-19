

class VisualMenu:

    def __init__(self, name=""):
        self.name = name
        self.menus = []
        self.items = []

    def getName(self):
        """:rtype: str"""
        return self.name

    def getMenus(self):
        """:rtype: list of VisualMenu"""
        return self.menus

    def getItems(self):
        """:rtype: list of VisualMenuItem"""
        return self.items

    def addMenu(self, menu):
        """:param VisualMenu menu:"""
        self.menus.append(menu)

    def addItem(self, item):
        """:param VisualMenuItem item: """
        self.items.append(item)

    def addItemIntoSubMenu(self, item, trace):
        """
        :param VisualMenuItem item:
        :param str trace:
        """
        trace_list = trace.split('.')
        current_menu = self
        for menu_name in trace_list:
            submenu_search = current_menu.getMenuWithName(menu_name)
            if submenu_search is not None:
                current_menu = submenu_search
            else:
                new_menu = VisualMenu(menu_name)
                current_menu.addMenu(new_menu)
                current_menu = new_menu

        current_menu.addItem(item)

    def getItemWithKeyword(self, keyword):
        """
        :param str keyword:
        :rtype: VisualMenuItem or None
        """
        for item in self.getItems():
            if item.getKeyword() == keyword:
                return item
        return None

    def getMenuWithName(self, name):
        """
        :param str name:
        :rtype: VisualMenu or None
        """
        for menu in self.getMenus():
            if menu.getName() == name:
                return menu
        return None


class VisualMenuItem:

    def __init__(self, keyword, value, text, input_type="", input_caption="", input_options=[]):
        self.keyword = keyword
        self.value = value
        self.text = text
        #
        self.input_type = input_type  # '' or 'select' or 'int' or 'float' or 'str'
        self.input_caption = input_caption
        self.input_options = input_options

    def getKeyword(self):
        """:rtype: str"""
        return self.keyword

    def getText(self):
        """:rtype: str"""
        return self.text

    def getValue(self):
        """:rtype: str"""
        return self.value

    def getInputType(self):
        """:rtype: str"""
        return self.input_type

    def getInputCaption(self):
        """:rtype: str"""
        return self.input_caption

    def getInputOptions(self):
        """:rtype: list of str"""
        return self.input_options
