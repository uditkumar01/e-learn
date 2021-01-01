# from urlextract import URLExtract

# def anchorUrl(text):
# 	extractor = URLExtract()
# 	urls = extractor.find_urls(text)
# 	for link in urls:
# 		x1 = text.find(link)
# 		y1 = x1+len(link)
# 		text = text[:y1]+ "</a>" +text[y1:]
# 		text = (text[:x1]+ "<a"+' href="'+link+'" style="text-decoration:none; color: #48dbfb;">' +text[x1:])
		
# 	return text

# print(anchorUrl("Text with URLs. Let's have URL google.com as an https://google.com example."))

# import pandas as pd
 
# # intialise data of lists.

# data = {'Item':['item_1','item_1','item_1','item_2','item_2','item_2'],
#         'Store':['A','B','C','A','B','C'],
#         'Quantity sold':[10.0,20.0,0.0,5.0,10.0,15.0]}
 
# # Create DataFrame
# df = pd.DataFrame(data)
# # df.index = ['R1', 'R2', 'R3', 'R4'] 
# # Print the output.
# print(df.groupby('Item').sum().iloc[0]['Quantity sold'])

import mimetypes
# mimetypes.init()

mimestart = mimetypes.guess_type("your_gift.txt")[0]
print(mimestart)
if mimestart != None:
    mimestart = mimestart.split('/')[0]

    if mimestart == 'audio' or mimestart == 'video' or mimestart == 'image':
        print("media types")