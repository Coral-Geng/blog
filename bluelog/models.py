# -*- coding: utf-8 -*-
"""
    :author: Grey Li (李辉)
    :url: http://greyli.com
    :copyright: © 2018 Grey Li <withlihui@gmail.com>
    :license: MIT, see LICENSE for more details.
"""
from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from bluelog.extensions import db


# 管理员模型
class Admin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20))
    password_hash = db.Column(db.String(128))
    blog_title = db.Column(db.String(60))
    blog_sub_title = db.Column(db.String(100))
    name = db.Column(db.String(30))
    about = db.Column(db.Text)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)

# 分类模型
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # 参数unique，唯一性，不能重复
    name = db.Column(db.String(30), unique=True)

    # 函数relationship() 定义两个表之间的关系
    # 参数back_populates 的作用是在对象中建立一个相互的参照
    # back_populates 需要在两个表中同时维护关系
    posts = db.relationship('Post', back_populates='category')
    # 而backref 参数提供了一种简化的方式（在一对多的一方维护就行)
    #  backref是老式的方法，back_populates是新式的方法，但是目前都可以使用

    def delete(self):
        default_category = Category.query.get(1)
        posts = self.posts[:]
        for post in posts:
            post.category = default_category
        db.session.delete(self)
        db.session.commit()

# 文章模型
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    can_comment = db.Column(db.Boolean, default=True)

    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.relationship('Category', back_populates='posts')
    # 参数cascade，设置关联数据的操作
    # all：是对save-update, merge, refresh-expire, expunge, delete几种的缩写。
    # delete-orphan级联删除
    comments = db.relationship('Comment', back_populates='post', cascade='all, delete-orphan')

# 评论模型
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(30))
    email = db.Column(db.String(254))
    site = db.Column(db.String(255))
    body = db.Column(db.Text)
    # 管理员评论
    from_admin = db.Column(db.Boolean, default=False)
    # 管理员审核
    reviewed = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # 在‘多’的一侧定义外键，指向“一”那一侧联接的记录
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    post = db.relationship('Post', back_populates='comments')

    # 邻接列表关系，在同一个模型内的一对多关系
    # 添加一个外键指向自身，这样就得到一种层级关系
    replied_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
    replies = db.relationship('Comment', back_populates='replied', cascade='all, delete-orphan')
    # 关系的两侧都在同一个模型中，SQLAlchemy无法分别关系的两侧
    # 通过将参数remote_side设为模型id字段，把id字段定义为关系的远程侧，即‘一’的一侧
    replied = db.relationship('Comment', back_populates='replies', remote_side=[id])
    # Same with:
    # replies = db.relationship('Comment', backref=db.backref('replied', remote_side=[id]),
    # cascade='all,delete-orphan')

# 友链模型
class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    url = db.Column(db.String(255))
