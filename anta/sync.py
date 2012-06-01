import os
import sys
import mimetypes
from datetime import datetime

path = '/var/www/sven.densitydesign.org'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'sven.settings'

from django.conf import settings
from optparse import OptionParser
from sven.anta.models import *

def sync( options, parser ):
	# dir to sync
	path = settings.MEDIA_ROOT + options.corpus
	
	# list files
	print "[sync] corpus:",options.corpus
	print "[sync] corpsu path:", path
	print "[sync] path exists:", os.path.exists( path )
	
	if not os.path.exists( path ):
		error( message="path created using corpus name does not exist!", parser=parser )
	
	# get or store corpus
	try:
		corpus = Corpus.objects.get( name=options.corpus )
	except:
		corpus = Corpus( name=options.corpus )
		corpus.save()
	
	# list document in corpus folder
	docs = os.listdir(path)
	
	for doc in docs:
		parts = os.path.splitext(doc)[0].split("_",3)
		mime_type	=  mimetypes.guess_type( path + "/" + doc )[0]
		
		if len( parts ) != 4:
			print "[sync] file name is not valid! skipping...", parts
			continue
		
		actors		= parts[0].split("-")
		language	= parts[1]
		try:
			date	= datetime.strptime( parts[2], "%Y%m%d" ) 
		except:
			print "[sync] date forma is not standard, substitute with datetime.now"
			date	= datetime.now()
			
		title		= parts[3].replace("_"," ")
		
		
		print
		print "[sync] saving file:", doc, mime_type
		print "[sync] file title:", title		
		print "[sync] file lang:", language
		print "[sync] file date:", date
		
		# get tags
		# tag rule, by underscore (actor(s)[minus spaced], lang[EN|NL|FR], data[YYYYMMDD], title )
		# ACTOR1-ACTOR2_EN_
		# underscore groups
		print actors
		
		# save documents
		try:
			d = Document.objects.get( url=doc )
			print "[sync] file already stored"

		except:
			# file do not exist, ty to uppload it
			d = Document( url=doc, mime_type=mime_type, ref_date=date, corpus=corpus, status='IN', language=language, title=title )
			print "[sync] file now added"
		
		# store actors as tags and attach with document_tags
		for a in actors:
			
			# create tag / retrieve aldready created one
			try:
				t = Tag.objects.get( name=a )
			except:
				t = Tag( name=a )
				t.save()
			
			try:
				dt = Document_Tag( document=d, tag=t )
				dt.save()
			except:
				continue
			
			
		# register modification
		d.save()
			
		# parse documents
		
		
			
def error( parser=None, message="generic error" ):
	print message
	if parser is not None:
		parser.print_help()
	exit(-1)

def main( argv):
	usage = "usage: %prog -c corpus_name -l lang"
	parser = OptionParser( usage=usage )
	parser.add_option(
		"-c", "--corpus", dest="corpus",
		help="write anta corpus_name to be sync. Every file under your MEDIA_ROOT/corpus_name folder will be recorded into the database if their name isn't already indexed")
	parser.add_option(
		"-l", "--lang", dest="language",
		default="EN",
		help="corpus language (char=2), e.g 'nl' or 'en', default 'en'. will be saved only for NEWLY added documents")
	( options, argv ) = parser.parse_args()
	
	
	if options.corpus is None:
		error( message="Use -c to specify the corpus", parser=parser )
	
		
	sync(options, parser )




if __name__ == '__main__':
	# get corpus name
	main(sys.argv[1:])