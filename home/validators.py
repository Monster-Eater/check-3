from django.core.exceptions import ValidationError

def file_size(value):
    filesize=value.size
    if filesize>419430400:
        raise ValidationError("Sorry...! Maximum video size shoould be 50mb")