import bookmarks_parser.parser as parser


def main():
    # set the bookmarks file path/name
    bookmarks_file_name = "bookmarks.html"

    result = parser.parse_file(file_name=bookmarks_file_name)
    print 'result', result


if __name__ == "__main__":
    main()
