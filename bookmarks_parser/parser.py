from bs4 import BeautifulSoup


def get_node_data(node):
    data = {}

    for child in node.children:
        if child.name == "a":

            data["type"] = "bookmark"
            data["url"] = child.attrs.get("href")
            data["title"] = child.text

            if child.attrs.get("add_date"):
                data["add_date"] = child.attrs.get("add_date")

            if child.attrs.get("icon"):
                data["icon"] = child.attrs.get("icon")

        elif child.name == "h3":
            data["type"] = "folder"
            data["title"] = child.text

            if child.attrs.get("add_date"):
                data["add_date"] = child.attrs.get("add_date")

            if child.attrs.get("last_modified"):
                data["last_modified"] = child.attrs.get("last_modified")

            data["ns_root"] = None
            if "personal_toolbar_folder" in child.attrs:
                data["ns_root"] = "toolbar"
            elif "unfiled_bookmarks_folder" in child.attrs:
                data["ns_root"] = "unsorted"

        elif child.name == "dl":
            # store DL element reference for further processing the child nodes
            data["__dir_dl"] = child

    # if current item is a folder, but we haven't found DL element for it inside the DT element - check if the next sibling is DD
    # and if so check if it has DL element if yes - we just found the DL element for the folder
    if data.get("type") == "folder" and not data.get("__dir_dl"):
        if node.next_sibling and node.next_sibling.name == "dd" and node.next_sibling.find("dl"):
            data["__dir_dl"] = node.next_sibling.find("dl")
        # elif node.next_sibling.name == "dl":
        #     data["__dir_dl"] = node.next_sibling

    return data


def process_dir(dir, level=0):
    menu_root = None

    items = []

    for child in dir.children:
        tag_name = child.name
        if tag_name != "dt":
            continue

        node_data = get_node_data(child)

        if node_data.get("type"):
            node_type = node_data.get("type")
            if level == 0 and not node_data.get("ns_root"):
                if not menu_root:
                    menu_root = {
                        "title": "Menu",
                        "children": [],
                        "ns_root": "menu"
                    }

                if node_type == "folder" and node_data.get("__dir_dl"):
                    node_data["children"] = process_dir(node_data.get("__dir_dl"), level=level + 1)
                    del node_data["__dir_dl"]

                menu_root["children"].append(node_data)
            else:
                if node_type == "folder" and node_data.get("__dir_dl"):
                    node_data["children"] = process_dir(node_data.get("__dir_dl"), level=level + 1)
                    del node_data["__dir_dl"]

                items.append(node_data)

    if menu_root:
        items.append(menu_root)

    return items


def parse(bookmarks_html):
    # parse the file text to bs4 object
    soup = BeautifulSoup(bookmarks_html, "html5lib")
    dls = soup.find_all("dl")
    if not dls:
        raise Exception("Bookmarks file malformed")

    dl = dls[0]
    return process_dir(dl)


def parse_file(file_name):
    # read the content of bookmarks file
    with open(file_name, "r") as f:
        bookmarks_html = f.read()

    return parse(bookmarks_html)

