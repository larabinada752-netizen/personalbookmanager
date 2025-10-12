"""
book_manager.py
Personal Book Manager CLI
Features: Add, list, search, update, delete, sort, export/import, JSON storage.
Suitable for intermediate-level GitHub projects.
"""
import json
import os
import datetime

FILENAME = "books.json"

# ---------- File Handling ----------
def load_books():
    if not os.path.exists(FILENAME):
        return []
    try:
        with open(FILENAME, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        print("Warning: Could not read books file, starting with an empty list.")
        return []

def save_books(books):
    try:
        with open(FILENAME, "w", encoding="utf-8") as f:
            json.dump(books, f, ensure_ascii=False, indent=2)
    except IOError as e:
        print(f"Error saving data: {e}")

# ---------- Helper Functions ----------
def input_nonempty(prompt):
    while True:
        v = input(prompt).strip()
        if v:
            return v
        print("This field cannot be empty. Please try again.")

def parse_year(year_str):
    year_str = year_str.strip()
    if not year_str:
        return ""
    if year_str.isdigit():
        y = int(year_str)
        current = datetime.datetime.now().year
        if 0 < y <= current:
            return str(y)
    print("Invalid or future year. Field will be left blank.")
    return ""

def print_book(index, book):
    print(f"{index}. \"{book.get('title')}\" — {book.get('author','Unknown')} ({book.get('year','N/A')}) | {book.get('category','General')}")
    if book.get("notes"):
        print(f"    Notes: {book['notes']}")

# ---------- Core Functions ----------
def list_books(books):
    if not books:
        print("\nNo books available.\n")
        return
    print("\n=== Book List ===")
    for i, b in enumerate(books, 1):
        print_book(i, b)
    print()

def add_book(books):
    print("\n--- Add a New Book ---")
    title = input_nonempty("Title: ")
    author = input("Author (optional): ").strip()
    year = parse_year(input("Year (optional): "))
    category = input("Category (optional, default 'General'): ").strip() or "General"
    notes = input("Notes (optional): ").strip()
    book = {
        "title": title,
        "author": author or "Unknown",
        "year": year,
        "category": category,
        "notes": notes
    }
    books.append(book)
    save_books(books)
    print("✅ Book added successfully!\n")

def find_books(books, keyword):
    k = keyword.lower().strip()
    results = []
    for i, b in enumerate(books, 1):
        if (k in b.get("title","").lower()
            or k in b.get("author","").lower()
            or k in b.get("category","").lower()):
            results.append((i, b))
    return results

def search_books(books):
    print("\n--- Search Books ---")
    q = input("Enter keyword (title, author, or category): ").strip()
    if not q:
        print("No search keyword entered.\n")
        return
    results = find_books(books, q)
    if not results:
        print("❌ No results found.\n")
        return
    print(f"\nFound {len(results)} result(s):")
    for idx, book in results:
        print_book(idx, book)
    print()

def choose_book_by_index(books, action_name="select"):
    if not books:
        print("No books available.\n")
        return None
    list_books(books)
    try:
        idx = int(input(f"Enter the book number to {action_name}: ").strip())
    except ValueError:
        print("Invalid input.\n")
        return None
    if 1 <= idx <= len(books):
        return idx - 1
    print("Number out of range.\n")
    return None

def update_book(books):
    print("\n--- Update a Book ---")
    method = input("Search by keyword (s) or enter number directly (n)? [s/n]: ").lower().strip() or "s"
    chosen = None
    if method == "s":
        q = input("Enter keyword to find the book: ").strip()
        matches = find_books(books, q)
        if not matches:
            print("No matches found.\n"); return
        print("Search results:")
        for idx, book in matches:
            print_book(idx, book)
        try:
            pick = int(input("Enter the result number to update: ").strip())
        except ValueError:
            print("Invalid input.\n"); return
        for idx, _ in matches:
            if idx == pick:
                chosen = idx - 1
                break
    else:
        chosen = choose_book_by_index(books, "update")

    if chosen is None:
        return

    book = books[chosen]
    print("\nLeave field empty to keep current value.")
    new_title = input(f"Title [{book['title']}]: ").strip() or book['title']
    new_author = input(f"Author [{book.get('author','Unknown')}]: ").strip() or book.get('author','Unknown')
    new_year = input(f"Year [{book.get('year','')}]: ").strip()
    new_year = parse_year(new_year) or book.get('year','')
    new_category = input(f"Category [{book.get('category','General')}]: ").strip() or book.get('category','General')
    new_notes = input(f"Notes [{book.get('notes','')}]: ").strip() or book.get('notes','')

    book.update({
        "title": new_title,
        "author": new_author,
        "year": new_year,
        "category": new_category,
        "notes": new_notes
    })
    save_books(books)
    print("✅ Book updated successfully!\n")

def delete_book(books):
    print("\n--- Delete a Book ---")
    chosen = choose_book_by_index(books, "delete")
    if chosen is None:
        return
    book = books[chosen]
    confirm = input(f"Are you sure you want to delete \"{book['title']}\"? (y/n): ").lower().strip()
    if confirm == "y":
        removed = books.pop(chosen)
        save_books(books)
        print(f"Deleted: {removed['title']}\n")
    else:
        print("Deletion cancelled.\n")

def sort_books(books):
    if not books:
        print("No books to sort.\n"); return
    print("\nSort options:")
    print("1. By Title (A-Z)")
    print("2. By Author (A-Z)")
    print("3. By Year (Newest first)")
    print("4. By Category")
    choice = input("Choose sort option (1-4): ").strip()
    if choice == "1":
        books.sort(key=lambda b: b.get("title","").lower())
    elif choice == "2":
        books.sort(key=lambda b: b.get("author","").lower())
    elif choice == "3":
        books.sort(key=lambda b: int(b.get("year") or 0), reverse=True)
    elif choice == "4":
        books.sort(key=lambda b: b.get("category","").lower())
    else:
        print("Invalid choice.\n"); return
    save_books(books)
    print("✅ Books sorted and saved.\n")

def export_books(books):
    if not books:
        print("No books to export.\n"); return
    fname = input("Enter export filename (e.g., export.json): ").strip() or "export.json"
    try:
        with open(fname, "w", encoding="utf-8") as f:
            json.dump(books, f, ensure_ascii=False, indent=2)
        print(f"✅ Exported to {fname}\n")
    except IOError as e:
        print(f"Export failed: {e}\n")

def import_books(books):
    fname = input("Enter JSON file path to import: ").strip()
    if not os.path.exists(fname):
        print("File does not exist.\n"); return
    try:
        with open(fname, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            added = 0
            for item in data:
                if not any(item.get("title")==b.get("title") and item.get("author")==b.get("author") and item.get("year")==b.get("year") for b in books):
                    books.append(item)
                    added += 1
            save_books(books)
            print(f"✅ Imported {added} book(s) (duplicates ignored).\n")
        else:
            print("Invalid file format. Must be a JSON list.\n")
    except (json.JSONDecodeError, IOError) as e:
        print(f"Import failed: {e}\n")

# ---------- Main CLI ----------
def main():
    books = load_books()
    while True:
        print("=== Personal Book Manager ===")
        print("1. List all books")
        print("2. Add a book")
        print("3. Search books")
        print("4. Update a book")
        print("5. Delete a book")
        print("6. Sort books")
        print("7. Export books to JSON")
        print("8. Import books from JSON")
        print("9. Exit")
        choice = input("Choose an option (1-9): ").strip()
        if choice == "1":
            list_books(books)
        elif choice == "2":
            add_book(books)
        elif choice == "3":
            search_books(books)
        elif choice == "4":
            update_book(books)
        elif choice == "5":
            delete_book(books)
        elif choice == "6":
            sort_books(books)
        elif choice == "7":
            export_books(books)
        elif choice == "8":
            import_books(books)
        elif choice == "9":
            print("Goodbye 👋"); break
        else:
            print("Invalid choice. Try again.\n")

if __name__ == "__main__":
    main()
