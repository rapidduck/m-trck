import json
string = r"""{'title': 'Komi-San Wa Komyushou Desu', 'description': "Komi-san is the beautiful and admirable girl that no-one can take their eyes off her. Almost the whole school sees her as the cold beauty out of their league, but Tadano Shigeo knows the truth: she's just really bad at communicating with others. Komi-san, who wishes to fix this bad habit of hers, tries to improve it with the help of Tadano-kun.", 'status': 'Ongoing', 'latest_chapter': 342.0, 'thumbnail': 'https://avt.mkklcdnv6temp.com/25/s/2-1583466695.jpg', 'website': 'read.mangabat.com'}""".replace("'", '"')
dict = json.loads(string)
print(dict)
print(type(dict))