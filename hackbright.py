"""Hackbright Project Tracker.

A front-end for a database that allows users to work with students, class
projects, and the grades students receive in class projects.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
db = SQLAlchemy()


def connect_to_db(app):
    """Connect the database to our Flask app."""

    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///hackbright'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


def get_student_by_github(github):
    """Given a GitHub account name, print info about the matching student."""

    QUERY = """
        SELECT first_name, last_name, github
        FROM students
        WHERE github = :github
        """

    db_cursor = db.session.execute(QUERY, {'github': github})

    row = db_cursor.fetchone()

    print("Student: {} {}\nGitHub account: {}".format(row[0], row[1], row[2]))


def make_new_student(first_name, last_name, github):
    """Add a new student and print confirmation.

    Given a first name, last name, and GitHub account, add student to the
    database and print a confirmation message.
    """
    QUERY = """ INSERT INTO students (first_name, last_name, github)
                VALUES(:firstname, :lastname, :github)
                """
    db.session.execute(QUERY, {'firstname': first_name,
                               'lastname': last_name,
                               'github': github})
    db.session.commit()
    print("Congrats, you have successfully added a student!")


def get_project_by_title(title):
    """Given a project title, print information about the project."""

    QUERY = """ SELECT title, description, max_grade 
                FROM projects
                WHERE title = :title
                """

    db_cursor = db.session.execute(QUERY, {'title': title})

    row = db_cursor.fetchone()

    print(f"Title:{row[0]}\nDescription:{row[1]}\nMax grade:{row[2]}")


def get_grade_by_github_title(github, title):
    """Print grade student received for a project."""

    QUERY = """SELECT student_github FROM grades WHERE student_github = :github
                """

    db_cursor = db.session.execute(QUERY, {'github': github})
    new_row = db_cursor.fetchone()

    if new_row is None:
        print("Sorry, name not valid")
        return

    QUERY = """SELECT project_title FROM grades WHERE project_title = :title
                """

    db_cursor = db.session.execute(QUERY, {'title': title})
    new_row = db_cursor.fetchone()

    if new_row is None:
        print("Sorry, title not valid")
        return

    QUERY = """SELECT grade
                FROM grades
                WHERE  student_github = :github AND project_title = :title
                """
    db_cursor = db.session.execute(QUERY, {'github': github, 'title': title})
    print(db_cursor)
    new_row = db_cursor.fetchone()
    print(new_row)
    if new_row is None:
        print("Student github or project title is not valid")
    else:
        print(f"Grade: {new_row[0]}")


def assign_grade(github, title, grade):
    """Assign a student a grade on an assignment and print a confirmation."""
    
    QUERY = """ INSERT INTO grades (student_github, project_title, grade)
                VALUES (:github, :title, :grade)
                """

    db.session.execute(QUERY, {'github': github, 'title': title, 'grade': grade})
    db.session.commit()

    print("Success!")


def add_project(title, description, max_grade):
    """Create a new project entry and print a confirmation."""

    QUERY = """ INSERT INTO projects (title, description, max_grade)
                VALUES (:title, :description, :max_grade)
                """

    db.session.execute(QUERY, {'title': title, 'description': description,
                               'max_grade': max_grade})
    db.session.commit()

    print("Success")


def see_all_grades(github):
    """Display project grades for students."""

    QUERY = """SELECT project_title, grade 
                FROM grades
                WHERE student_github = :github"""

    cursor = db.session.execute(QUERY, {'github': github})

    new_row = cursor.fetchall()

    for item in new_row:
        print(f"{item[0]}: {item[1]}")


def handle_input():
    """Main loop.

    Repeatedly prompt for commands, performing them, until 'quit' is received
    as a command.
    """

    command = None

    while command != "quit":
        input_string = input("HBA Database> ")
        tokens = input_string.split()
        command = tokens[0]
        args = tokens[1:]

        if command == "student":
            github = args[0]
            get_student_by_github(github)

        elif command == "new_student":
            first_name, last_name, github = args  # unpack!
            make_new_student(first_name, last_name, github)

        elif command == "project_title":
            title = args[0]
            get_project_by_title(title)

        elif command == "grade_by_github_title":
            github, title = args
            get_grade_by_github_title(github, title)

        elif command == "assign_grade":
            github, title, grade = args
            assign_grade(github, title, grade)

        elif command == "add_project":
            title = args[0]
            grade = args[-1]
            description = args[1:-1]
            description = ' '.join(description)

            add_project(title, description, grade)

        else:
            if command != "quit":
                print("Invalid Entry. Try again.")


if __name__ == "__main__":
    connect_to_db(app)

    handle_input()

    # To be tidy, we close our database connection -- though,
    # since this is where our program ends, we'd quit anyway.

    db.session.close()
