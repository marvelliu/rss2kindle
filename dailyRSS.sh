mkdir -p /tmp/kindle

rm -rf /tmp/kindle/*
cd server && python check.py ../channels/tech.txt "Tech"

#rm -rf /tmp/kindle/*
#cd server && python check.py ../channels/news.txt "News"
