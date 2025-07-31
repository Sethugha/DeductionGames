import json
dicts=[]
keys = ["metamorphosis", "hint_request", "character_request", "interrogation", "accusation", "indicators"]
id=1
for key in keys:
    with open(f"Sources/basic_prompts/{id}.txt", 'r') as infile:
        content = infile.read()
    dicts.append({"title": key, "content": content})
    id+=1

id=1
for dict in dicts:
    filename="Sources/basic_prompts/prompt"+str(id)+".json"
    with open(filename, "w") as jf:
        json.dump(dict, jf, indent=4)
    id +=1
