from collections import UserDict
from datetime import datetime, timedelta
import pickle


def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)


def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)

        except ValueError as e:
            return str(e)

        except KeyError:
            return "Contact not found."

        except AttributeError:
            return "Contact not found."

        except IndexError:
            return "Not enough arguments."

    return inner


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value):
        if not (value.isdigit() and len(value) == 10):
            raise ValueError(
                "Phone number must contain exactly 10 digits."
            )

        super().__init__(value)


class Birthday(Field):
    def __init__(self, value):
        try:
            datetime.strptime(
                value,
                "%d.%m.%Y"
            )

            super().__init__(value)

        except ValueError:
            raise ValueError(
                "Invalid date format. Use DD.MM.YYYY"
            )


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone_number):
        phone = Phone(phone_number)
        self.phones.append(phone)

    def remove_phone(self, phone_number):
        phone = self.find_phone(phone_number)

        if phone:
            self.phones.remove(phone)

    def edit_phone(self, old_number, new_number):
        phone = self.find_phone(old_number)

        if phone is None:
            raise ValueError(
                "Old phone number not found."
            )

        new_phone = Phone(new_number)
        phone.value = new_phone.value

    def find_phone(self, phone_number):
        for phone in self.phones:
            if phone.value == phone_number:
                return phone

        return None

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        phones = "; ".join(
            phone.value for phone in self.phones
        )

        birthday = (
            self.birthday.value
            if self.birthday
            else "No birthday"
        )

        return (
            f"{self.name.value}: "
            f"{phones}, Birthday: {birthday}"
        )


class AddressBook(UserDict):

    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self):
        today = datetime.today().date()
        upcoming_birthdays = []

        for record in self.data.values():

            if record.birthday is None:
                continue

            birthday = datetime.strptime(
                record.birthday.value,
                "%d.%m.%Y"
            ).date()

            birthday_this_year = birthday.replace(
                year=today.year
            )

            if birthday_this_year < today:
                birthday_this_year = (
                    birthday_this_year.replace(
                        year=today.year + 1
                    )
                )

            days_diff = (
                birthday_this_year - today
            ).days

            if 0 <= days_diff <= 7:

                congratulation_date = (
                    birthday_this_year
                )

                if congratulation_date.weekday() == 5:
                    congratulation_date += timedelta(
                        days=2
                    )

                elif congratulation_date.weekday() == 6:
                    congratulation_date += timedelta(
                        days=1
                    )

                upcoming_birthdays.append(
                    {
                        "name": record.name.value,
                        "birthday": congratulation_date.strftime(
                            "%d.%m.%Y"
                        ),
                    }
                )

        return upcoming_birthdays

    def __str__(self):
        if not self.data:
            return "No contacts found."

        return "\n".join(
            str(record)
            for record in self.data.values()
        )


def parse_input(user_input):
    cmd, *args = user_input.split()
    return cmd.strip().lower(), args


@input_error
def add_contact(args, book):
    name, phone, *_ = args

    record = book.find(name)

    message = "Contact updated."

    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."

    if phone:
        record.add_phone(phone)

    return message


@input_error
def change_contact(args, book):
    name, old_phone, new_phone = args

    record = book.find(name)

    record.edit_phone(
        old_phone,
        new_phone
    )

    return "Contact updated."


@input_error
def show_phone(args, book):
    name = args[0]

    record = book.find(name)

    return "; ".join(
        phone.value
        for phone in record.phones
    )


@input_error
def delete_contact(args, book):
    name = args[0]

    if book.find(name) is None:
        raise KeyError

    book.delete(name)

    return "Contact deleted."


@input_error
def add_birthday(args, book):
    name, birthday = args

    record = book.find(name)

    record.add_birthday(birthday)

    return "Birthday added."


@input_error
def show_birthday(args, book):
    name = args[0]

    record = book.find(name)

    if record.birthday is None:
        return "Birthday not set."

    return record.birthday.value


@input_error
def birthdays(args, book):
    upcoming = book.get_upcoming_birthdays()

    if not upcoming:
        return "No birthdays in the next 7 days."

    result = []

    for user in upcoming:
        result.append(
            f"{user['name']} -> "
            f"{user['birthday']}"
        )

    return "\n".join(result)


def show_all(book):
    return str(book)


def main():
    book = load_data()

    print("Welcome to the assistant bot!")

    while True:
        user_input = input(
            "Enter a command: "
        )

        if not user_input:
            print("Invalid command.")
            continue

        try:
            command, args = parse_input(
                user_input
            )

        except ValueError:
            print("Invalid command.")
            continue

        if command in ["close", "exit"]:
            save_data(book)
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            result = add_contact(args, book)
            save_data(book)
            print(result)

        elif command == "change":
            result = change_contact(args, book)
            save_data(book)
            print(result)

        elif command == "phone":
            print(
                show_phone(
                    args,
                    book
                )
            )

        elif command == "delete":
            result = delete_contact(args, book)
            save_data(book)
            print(result)

        elif command == "all":
            print(show_all(book))

        elif command == "add-birthday":
            result = add_birthday(args, book)
            save_data(book)
            print(result)

        elif command == "show-birthday":
            print(
                show_birthday(
                    args,
                    book
                )
            )

        elif command == "birthdays":
            print(
                birthdays(
                    args,
                    book
                )
            )

        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()