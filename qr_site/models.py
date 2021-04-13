from flask_login import UserMixin
# from qr_site import db
# from sqlalchemy.dialects import mysql


# class Users(db.Model):
#     id = db.Column('u_id', mysql.INTEGER, primary_key=True)
#     email = db.Column('u_email', mysql.MEDIUMTEXT, nullable=False)
#     password = db.Column('u_password', mysql.VARCHAR(256), nullable=False)
#     name = db.Column('u_name', mysql.MEDIUMTEXT, nullable=False)
#     surname = db.Column('u_surname', mysql.MEDIUMTEXT, nullable=False)
#     patronymic = db.Column('u_patronymic', mysql.MEDIUMTEXT, nullable=True)
#     privilege_id = db.Column('u_privilege_id', mysql.INTEGER, db.ForeignKey('privileges.p_id'))
#     photo = db.Column('u_photo', mysql.MEDIUMTEXT, nullable=True)
#     additional_data = db.Column('u_additional_data', mysql.MEDIUMTEXT, nullable=True)
#
#     def is_authenticated(self):
#         return True
#
#     def is_active(self):
#         return True
#
#     def is_anonymous(self):
#         return False
#
#     def get_id(self):
#         return self.id
#
#     def __init__(self):
#         try:
#             self.id = Users.query.order_by(Users.id.desc()).first().id + 1
#         except AttributeError:
#             self.id = 1


class User():

    # id = db.Column(db.Integer, primory_key=True)
    # cookie = db.Column(db.Cookie, nullable=False)


    def __init__(self, id, cookie):
        self.id = id
        self.cookie = cookie

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id


    pass