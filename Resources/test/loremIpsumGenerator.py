import time

with open('/Volumes/Projetos/Git/logViewer/Resources/test/test.log', 'a') as log:
	count = 0
	while True:
		lines = 500
		count += 1
		for e in range(lines):
			log.write('Lorem ipsum ddescription du lore abdulis et dolores et dolor lore persisted per ignores.Lorem ipsum ddescription du lore abdulis et dolores et dolor lore persisted per ignores. Lorem ipsum ddescription du lore abdulis et dolores et dolor lore persisted per ignores. Lorem ipsum ddescription du lore abdulis et dolores et dolor lore persisted per ignores. Lorem ipsum ddescription du lore abdulis et dolores et dolor lore persisted per ignores.Lorem ipsum ddescription du lore abdulis et dolores et dolor lore persisted per ignores. Lorem ipsum ddescription du lore abdulis et dolores et dolor lore persisted per ignores. Lorem ipsum ddescription du lore abdulis et dolores et dolor lore persisted per ignores. Lorem ipsum ddescription du lore abdulis et dolores et dolor lore persisted per ignores.Lorem ipsum ddescription du lore abdulis et dolores et dolor lore persisted per ignores. Lorem ipsum ddescription du lore abdulis et dolores et dolor lore persisted per ignores. Lorem ipsum ddescription du lore abdulis et dolores et dolor lore persisted per ignores. Lorem ipsum ddescription du lore abdulis et dolores et dolor lore persisted per ignores.Lorem ipsum ddescription du lore abdulis et dolores et dolor lore persisted per ignores. Lorem ipsum ddescription du lore abdulis et dolores et dolor lore persisted per ignores. Lorem ipsum ddescription du lore abdulis et dolores et dolor lore persisted per ignores. Lorem ipsum ddescription du lore abdulis et dolores et dolor lore persisted per ignores.Lorem ipsum ddescription du lore abdulis et dolores et dolor lore persisted per ignores. Lorem ipsum ddescription du lore abdulis et dolores et dolor lore persisted per ignores. Lorem ipsum ddescription du lore abdulis et dolores et dolor lore persisted per ignores. Lorem ipsum ddescription du lore abdulis et dolores et dolor lore persisted per ignores.\n')
		print(f'Execution : {count}: {lines} generated')
		time.sleep(1)
