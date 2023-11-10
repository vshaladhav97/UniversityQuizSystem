from .models import *
import re

# register validations function
def registervalidations(params):
    error_message = ""
    if (params['first_name']).lower() in (params['password']).lower() or (params['last_name']).lower() in (params['password']).lower():
        error_message += "Ensure password does not contain first name or last name.#"

    if (params['username'] == "" or params['username'] == None):
        error_message += "username is required.#"

    if (params['email'] == "" or params['email'] == None):
        error_message += "email is required.#"

    if (params['first_name'] == "" or params['first_name'] == None):
        error_message += "first name is required.#"

    if (params['last_name'] == "" or params['last_name'] == None):
        error_message += "last name is required.#"

    if params['email']:
        given_string = params['email'].split("@")[1]
        if AutorizeMailerDomain.objects.filter(mail_domain_name = given_string):
            pass
        else:
            error_message += "please enter valid domain.#"

    if (params['password'] == "" or params['password'] == None):
        error_message += "password is required.#"

    # Password validation
    password = params.get('password', None)
    if not password:
        error_message += "password is required.#"
    elif len(password) < 8 or len(password) > 15:
        error_message += "Ensure password is between 8 and 15 characters.#"
    elif not re.match(r'^(?=.*[a-zA-Z])(?=.*\d)[A-Za-z\d]*$', password):
        error_message += "Ensure password is alphanumeric.#"

    if len(params['username']) < 3 or len(params['username']) >= 30:
        error_message += "Ensure username has at least 3 characters.#"

    if len(params['first_name']) < 3 or len(params['first_name']) >= 30:
        error_message += "Ensure first name has at least 3 character and maximum 30 character.#"

    if len(params['last_name']) < 3 or len(params['last_name']) >= 30:
        error_message += "Ensure last name has at least 3 character and maximum 30 character.#"

    if not params['role']:
        error_message += "Role cannot be empty"
    if str(params['role']).isdigit():
        error_message += "Role cannot be a number"
    if params['role'] not in ['Examiner', 'Examinee']:
        error_message += "Role must be 'Examiner' or 'Examinee'"

    return (error_message[:-1])
