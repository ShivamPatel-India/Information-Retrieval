# import BeautifulSoup
from bs4 import BeautifulSoup
import re

# HTML content (store it in a string)
html_content = """<!DOCTYPE html>
<html>
<head>
    <title>My first web page</title>
</head>
<body>
    <h1>My first web page</h1>
    <h2>What this is tutorial</h2>
    <p>A simple page put together using HTML. <em>I said a simple page.</em>.</p>
    <ul>
        <li>To learn HTML</li>
        <li>
            To show off
            <ol>
                <li>To my boss</li>
                <li>To my friends</li>
                <li>To my cat</li>
                <li>To the little talking duck in my brain</li>
            </ol>
        </li>
        <li>Because I have fallen in love with my computer and want to give her some HTML loving.</li>
    </ul>
    <h3>Where to find the tutorial</h3>
    <p><a href="http://www.aaa.com"><img src="http://www.aaa.com/badge1.gif"></a></p>
    <h4>Some random table</h4>
    <table>
        <tr class="tutorial1">
            <td>Row 1, cell 1</td>
            <td>Row 1, cell 2<img src="http://www.bbb.com/badge2.gif"></td>
            <td>Row 1, cell 3</td>
        </tr>
        <tr class="tutorial2">
            <td>Row 2, cell 1</td>
            <td>Row 2, cell 2</td>
            <td>Row 2, cell 3<img src="http://www.ccc.com/badge3.gif"></td>
        </tr>
    </table>
</body>
</html>"""


# ANSWER-A

# Parsing and printing title using 'title' tag
print(BeautifulSoup(html_content, 'html.parser').find('title').text)

# ANSWER-B

# Parsing and printing the second list item within the nested <ol> 
print(BeautifulSoup(html_content, 'html.parser').find_all(
    'ol')[0].find_all('li')[1].text)

# ANSWER-C

# Parsing and printing all <td> tags in the first <tr> of the table
print([td.text for td in BeautifulSoup(html_content, 'html.parser').find(
    'table').find_all('tr')[0].find_all('td')])

# ANSWER-D

# Parsing and printing all <h2> headings text that include the word "tutorial" using regular expression
print([h2.text for h2 in BeautifulSoup(html_content, 'html.parser').find_all(
    'h2', string=re.compile(r'tutorial'))])

# ANSWER-E

# Parsing and printing all text that includes the "HTML" word
# print([text for text in BeautifulSoup(html_content,'html.parser').find_all(string=re.compile(r'HTML'))])
print([text for text in BeautifulSoup(html_content,'html.parser').stripped_strings if "HTML" in text])

# ANSWER-F

# Parsing and printing all text in the second <tr> of the table
print([td.text for td in BeautifulSoup(html_content, 'html.parser').find(
    'table').find_all('tr')[1].find_all('td')])


# ANSWER-G

# Parsing and printing all <img> tags from the table
print([img['src'] for img in BeautifulSoup(
    html_content, 'html.parser').find('table').find_all('img')])
