x = "Familie Fl\u00f6z"

x = x.encode('utf-8').decode('unicode_escape').encode("latin1").decode("utf-8")
print(x)
with open("test.txt", "w") as f:
    f.write(x)