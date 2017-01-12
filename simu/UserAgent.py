import urllib
import re


ptrn = re.compile("<textarea name='uas' id='uas_textfeld' rows='4' cols='30'>(.+?)</textarea>")

with open("user_agent.txt", "w") as fp:
    for i in range(12381, 15480):
        try:
            url = "http://www.useragentstring.com/index.php?id=" + str(i)
            html = urllib.urlopen(url).read()
            user_agent = re.search(ptrn, html).group(1)
            fp.write(user_agent + "\n")
        except Exception:
            pass
