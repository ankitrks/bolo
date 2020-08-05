from haystack.management.commands import update_index


def run():
	update_index.Command().handle(age=1)