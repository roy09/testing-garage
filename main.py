import webapp2
import os
import jinja2
import re

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
								autoescape = True)
								
def render_str(template, **params):
	t = jinja_env.get_template(template)
	return t.render(params)

class BlogHandler(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)
		
	def render_str(self, template, **params):
		return render_str(template, **params)
		
		
	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))

class Post(db.Model):
	subject = db.StringProperty(required = True)
	content = db.StringProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)
	last_modified = db.DateTimeProperty(auto_now = True)
	
	def render(self):
		self._render_text = self.content.replace('\n', '<br>')
		return render_str("post.html", p = self)

class MainPage(BlogHandler):
    def get(self):
		posts = db.GqlQuery("select * from Post order by created desc limit 10")
		self.render("front.html", posts = posts)

class NewPost(BlogHandler):
	def get(self):
		self.render("newpost.html")
		
	def post(self):
		subject = self.request.get('subject')
		content = self.request.get('content')
		
		if subject and content:
			p = Post(subject = subject, content = content)
			p.put()
			self.redirect('/%s' % str(p.key().id()))
		else:
			error = "Both subject and content please!"
			self.render("newpost.html", subject = subject, content = content, error = error)

class Permalink(BlogHandler):
	def get(self, post_id):
		key = db.Key.from_path("Post", int(post_id))
		post = db.get(key)
		
		if not post:
			self.error(404)
			return
		
		self.render("permalink.html", post = post)
		
app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/newpost', NewPost),
    ('/([0-9]+)', Permalink),
], debug=True)
