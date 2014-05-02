LOGGED_IN_SIG=$(shell grep logged-in-sig ~/.config/internetarchive.yml | awk '{print $$2}')
DATE=$(shell date +'%Y-%m-%d')

items:
	find /Volumes/patent -type d -maxdepth 2 -mindepth 2 | parallel -j4 'python uspto_uploader.py {}'

itemlist.txt:
	curl --header 'Cookie: logged-in-sig=$(LOGGED_IN_SIG); logged-in-user=jake%40archive.org;' 'https://archive.org/metamgr.php?f=exportIDs&w_format=!Abbyy*&w_collection=uspto*&w_publicdate=%3E2014-05-01&w_curatestate=!dark%20OR%20null' -o 'itemlist-$(DATE).txt' -L
