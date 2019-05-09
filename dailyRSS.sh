mkdir -p /tmp/kindle

#rm -rf /tmp/kindle/*
cd server 
python check.py ../channels/tech.txt "Tech"
echo "hello" | mail -s "hello world" marvel1983@kindle.cn -A /tmp/kindle/daily.mobi

#rm -rf /tmp/kindle/*
python check.py ../channels/news.txt "News"
echo "hello" | mail -s "hello world" marvel1983@kindle.cn -A /tmp/kindle/daily.mobi
