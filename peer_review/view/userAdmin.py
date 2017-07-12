import csv
import os
from django.http import HttpResponseRedirect
from django.shortcuts import render
from peer_review.forms import DocumentForm, UserForm
from peer_review.models import User, Document
from peer_review.view.userFunctions import user_error
from peer_review.view.userManagement import create_user_send_otp


def add_csv_info(user_list):
    for row in user_list:
        module_dir = os.path.dirname(__file__)
        file_path = os.path.join(module_dir)
        file = open(file_path + '/../text/otp_email.txt', 'a+')
        file.seek(0)
        # email_text = file.read()
        file.close()

        user = create_user_send_otp(
            user_userId=row['user_id'],
            user_status='U',
            user_title=row['title'],
            user_initials=row['initials'],
            user_name=row['name'],
            user_surname=row['surname'],
            user_cell=row['cell'],
            user_email=row['email']
        )

        # Send OTP email
        user.save()
    return


def submit_csv(request):
    if not request.user.is_authenticated():
        return user_error(request)

    global errortype
    file_path = ""
    if request.method == 'POST':
        users = User.objects.all
        user_form = UserForm()
        doc_form = DocumentForm()

        module_dir = os.path.dirname(__file__)
        file_path = os.path.join(module_dir)
        file = open(file_path + '/../text/otp_email.txt', 'r+')
        email_text = file.read()
        file.close()
        form = DocumentForm(request.POST, request.FILES)

        test_flag = (request.POST["test-submit-flag"] == "1");

        if form.is_valid():
            newdoc = Document(docfile=request.FILES['docfile'])
            newdoc.save()

            file_path = newdoc.docfile.url
            file_path = file_path[1:]

            user_list = list()
            error = False

            # documents = Document.objects.all()

            count = 0
            with open(file_path, encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    valid = validate(row)
                    count += 1
                    if valid == 1:
                       user_list.append(row)
                        # ToDo check for errors in multiple rows
                    else:
                        error = True
                        if valid == 0:
                            message = "The format of the CSV is incorrect."
                            errortype = 0
                            return render(request, 'peer_review/userAdmin.html',
                                          {'message': message,
                                           'error': errortype,
                                           'users': users,
                                           'userForm': user_form,
                                           'docForm': doc_form,
                                           'email_text': email_text})
                        else:
                            message = str(count)

                            rowlist = list()
                            rowlist.append(row['title'])
                            rowlist.append(row['initials'])
                            rowlist.append(row['name'])
                            rowlist.append(row['surname'])
                            rowlist.append(row['email'])
                            rowlist.append(row['cell'])
                            rowlist.append(row['user_id'])

                        if valid == 2:
                            errortype = 2
                        if valid == 3:
                            errortype = 3
                        if valid == 4:
                            errortype = 4

                        csvfile.close()

                        if os.path.isfile(file_path):
                            os.remove(file_path)

                        return render(request, 'peer_review/userAdmin.html',
                                      {'message': message, 
                                           'row': rowlist, 
                                           'error': errortype, 
                                           'users': users,
                                           'userForm': user_form,
                                           'docForm': doc_form,
                                           'email_text': email_text})
        else:
            form = DocumentForm()
            message = "Oops! Something seems to be wrong with the CSV file."
            errortype = "No file selected."
            return render(request, 'peer_review/csvError.html', {'message': message, 'error': errortype})

        if not error:
            # todo: add confirmation dialog, and print out names of new users
            if not test_flag:
                add_csv_info(user_list)
                return render(request, 'peer_review/userAdmin.html',
                                      {'new_users': user_list,
                                           'users': users,
                                           'userForm': user_form,
                                           'docForm': doc_form,
                                           'email_text': email_text})
            else:
                return render(request, 'peer_review/userAdmin.html',
                                      {'possible_users': user_list,
                                           'users': users,
                                           'userForm': user_form,
                                           'docForm': doc_form,
                                           'email_text': email_text})

    if os.path.isfile(file_path):
        os.remove(file_path)
    return HttpResponseRedirect('../')


def validate(row):
    # 0 = incorrect number of fields
    # 1 = correct
    # 2 = missing value/s
    # 3 = incorrect format
    # 4 = user already exists

    if len(row) < 7:
        return 0

    for key, value in row.items():
        if value is None:
            return 2

    # for key, value in row.items():
    #     if key == "cell":
    #         try:
    #             int(value)
    #         except ValueError:
    #             return 3

    user = User.objects.filter(userId=row['user_id'])

    if user.count() > 0:
        return 4

    return 1