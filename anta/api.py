from django.http import HttpResponse, HttpRequest, HttpResponseRedirect
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from sven.anta.models import *
from django.conf import settings
from django.contrib.auth import login, logout
from django.core import serializers
import os, json, datetime

from sven.anta.utils import *
from sven.anta.forms import *
from django.contrib.auth.models import User
 
#
#    ========================
#    ---- JSON API CONST ----
#    ========================
#
API_LOGIN_REQUESTED_URL = '/sven/anta/api/login-requested'	 # needs to be logged in
API_ACCESS_DENIED_URL = '/sven/anta/api/access-denied'	 # needs to be logged in and th corpus should be cool
API_DEFAULT_OFFSET = 0
API_DEFAULT_LIMIT = 50
API_AVAILABLE_METHODS = [ 'PUT', 'DELETE', 'POST', 'GET' ]

API_EXCEPTION_DOESNOTEXIST =	'DoesNotExist'
API_EXCEPTION_FORMERRORS	=	'FormErrors'

#
#    ==================================
#    ---- ASSISTANT JSON API VIEWS ----
#    ==================================
#

def index(request):
	response = _json( request )
	#user = User.objects.create_user('daniele', 'lennon@thebeatles.com', 'danielepassword')
	#user.is_staff = True
	#user.save()
	return render_to_json( response )

def get_corpora(request):
	response = _json( request )
	response['objects']	= [ c.json() for c in Corpus.objects.all() ]
	return render_to_json( response )

def get_corpus(request, corpus_id ):
	response = _json( request )
	
	try:
		response['corpus'] = Corpus.objects.get(name=corpus_id).json()
	except:
		response['corpus'] = None
		return throw_error( response, "corpus does not exist...")
	
	
	return render_to_json( response )



@login_required( login_url = API_LOGIN_REQUESTED_URL )
def relations( request ):
	response = _json( request )

	# create documents
	if response['meta']['method'] == 'POST':
		return create_relation( request, response )
	
	if request.REQUEST.has_key( 'corpus' ):
		try:
			response['corpus'] = Corpus.objects.get(name=corpus).json()
		except:
			return throw_error( response, error="aje, corpus does not exist...")
		response['meta']['total'] = Relation.objects.filter( source__corpus__name=corpus, target__corpus__name=corpus).count()		
		response['results'] = [r.json() for r in Relation.objects.filter( source__corpus__name=corpus, target__corpus__name=corpus) [response['meta']['offset']:response['meta']['limit'] ]  ]
		return render_to_json( response )
	

	response['meta']['total'] = Relation.objects.count()
	response['results'] = [r.json() for r in Relation.objects.all()[ response['meta']['offset']:response['meta']['limit'] ] ]
	
	return render_to_json( response )

@login_required( login_url = API_LOGIN_REQUESTED_URL )
def create_relation( request, response ):
	response['owner'] = request.user.json()
	form = ApiRelationForm( request.REQUEST, initial={'owner':request.user} )
	if form.is_valid():
		r = Relation( 
			source=form.cleaned_data['source'], target=form.cleaned_data['target'],
			polarity=form.cleaned_data['polarity'],description=form.cleaned_data['description'], 
			owner=form.cleaned_data['owner']
		)
		r.save()
		response['created'] = r.json()
		return render_to_json( response )
	else:
		return throw_error( response, error=form.errors, code=API_EXCEPTION_FORMERRORS )

@login_required( login_url = API_LOGIN_REQUESTED_URL )
def relation( request, id ):
	response = _json( request )
	# all documents
	r =  _get_relation( id )
	if r is None:
		return throw_error( response, "Relation %s does not exist...," % id, code=API_EXCEPTION_DOESNOTEXIST )	
	
	response['results'] = [r.json()]
		
	if response['meta']['method'] == 'DELETE':
		r.delete()		
	
	
	return render_to_json( response )


#
#    ==================
#    ---- DOCUMENTS----
#    ==================
#	

@login_required( login_url = API_LOGIN_REQUESTED_URL )
def documents(request):
	response = _json( request )

	# create documents
	if response['meta']['method'] == 'POST':
		return create_document( request, response )
	
	
	if request.REQUEST.has_key( 'corpus' ):
		try:
			response['corpus'] = Corpus.objects.get(name=corpus).json()
		except:
			return throw_error( response, "aje corpus does not exist...")
		response['meta']['total'] = Document.objects.count()		
		response['results'] = [d.json() for d in Document.objects.filter( corpus__name=corpus )]
		return render_to_json( response )
	
	# all documents
	response['meta']['total'] = Document.objects.count()
	response['results'] = [d.json() for d in Document.objects.all()[ response['meta']['offset']:response['meta']['limit'] ] ]
	
	
	return render_to_json( response )

@login_required( login_url = API_LOGIN_REQUESTED_URL )
def create_document( request, response ):
	return throw_error( response, "unsupported method")
	

@login_required( login_url = API_LOGIN_REQUESTED_URL )
def document(request, document_id):
	response = _json( request )

	# create or update a document
	# @todo	

	d = _get_document( document_id )
	if d is None:
		return throw_error( response, "dcument does not exist...")
	
	text = textify( d, settings.MEDIA_ROOT )
	
	if text is None:
		return throw_error( response, "unable to provide txt version of the document")
	
	# f = open( text, "r")
		
	response['results'] = [ d.json() ]
	response['text']	= open(text, 'r').read()
	
	return render_to_json( response )


#
#    ======================
#    ---- OTHER STUFFS ----
#    ======================
#

@login_required( login_url = API_LOGIN_REQUESTED_URL )
def dummy_gummy( request ):
	# test only view, with request
	response = _json( request )
	return render_to_json( response )
	
def logout_view( request ):
	logout( request )
	response = _json( request )
	return render_to_json( response )
	

#
#    =======================
#    ---- ACCESS DENIED ----
#    =======================
#

def login_requested( request ):
	response = _json( request )
	return throw_error( response, error="you're not authenticated", code="auth failed" )





def access_denied( request ):
	response = _json( request )
	return throw_error( response, error="access denied", code="forbidden" )



#
#    ==========================
#    ---- API VIEW HELPERS ----
#    ==========================
#
#    try except handling on the road
#    Intended for Internal use only.
#

	

def _get_corpus( corpus, user=None ):
	# given a corpus name return None or a corpus object
	try:
		c = Corpus.objects.get(name=corpus)
		return c
	except:
		return None

def _get_document( document_id ):
	# given a document id return None or a corpus object
	try:
		d = Document.objects.get(id=document_id)
		return d
	except:
		return None

def _get_relation( relation_id ):
	# given a relation id return None or the related Relation object
	try:
		r = Relation.objects.get(id=relation_id)
		return r
	except:
		return None


def _json( request ):
	j =  {"status":"ok", 'meta':{ 'indent':False } }
	if request.REQUEST.has_key('indent'):
		j['meta']['indent'] = True

	form = ApiMetaForm( request.REQUEST )
	# get method
	if request.REQUEST.has_key('method'):
		j['meta']['method'] =  request.REQUEST.get('method')
	else:
		j['meta']['method'] = request.method

	if request.REQUEST.has_key('filters'):
		j['meta']['filters'] =  request.REQUEST.get('filters')
	else:
		j['meta']['filters'] = []

	# test against available methods, default with GET
	if not j['meta']['method']  in API_AVAILABLE_METHODS:
		j['meta']['method'] = 'GET'
		j['warnings'] = {'method':'default menthod GET applied, unhandled param "method" found in your request'}

	# offset, limit + next, prev like twitter 
	if j['meta']['method'] == 'GET':	

		if request.REQUEST.has_key('offset') or request.REQUEST.has_key('limit') :
			# check value
			if form.is_valid():
				j['meta']['offset']	= form.cleaned_data['offset'] if form.cleaned_data['offset'] else API_DEFAULT_OFFSET 
				j['meta']['limit']	= form.cleaned_data['limit'] if form.cleaned_data['limit'] else API_DEFAULT_LIMIT 
			else:
				j['meta']['offset']	= API_DEFAULT_OFFSET 
				j['meta']['limit']	= API_DEFAULT_LIMIT 
				j['meta']['errors']	= form.errors
		else:
			# default values
			j['meta']['offset']	= API_DEFAULT_OFFSET
			j['meta']['limit']	= API_DEFAULT_LIMIT 
		
		# next and prev like twitter, leverage inside their own view
		j['meta']['next'] = {
			'offset': j['meta']['offset'] + j['meta']['limit'],
			'limit':  j['meta']['limit']
		}
	
		if j['meta']['offset']	> 0:
			j['meta']['previous'] = {
				'offset': max( j['meta']['offset'] - j['meta']['limit'],  API_DEFAULT_OFFSET ),
				'limit': min( j['meta']['offset'],  j['meta']['limit'] )
			}
		


	
	if request.user is not None:
		j['user'] = request.user.username
	return j
	
def render_to_json( response ):
	if response['meta']['indent']:
		return HttpResponse( json.dumps( response, indent=4),  mimetype="text/plain")	
	return HttpResponse( json.dumps( response ),  mimetype="text/plain")



def throw_error( response, error="", status="ko", code="404", verbose="", friendly="" ):
	response[ 'error' ] = error # developer message
	response[ 'status' ] = status
	response[ 'errorCode' ] = code
	response[ 'userMessage' ] = friendly

	return render_to_json( response )
