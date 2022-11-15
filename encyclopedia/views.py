from django.shortcuts import render
from django.http import HttpResponseRedirect
from . import util
from django import forms
import markdown2
import random


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def entry(request, title):
    entry = util.get_entry(title)
    if entry:
        html = markdown2.markdown(entry)
        return render(request, "encyclopedia/entry.html", {
            "title": title,
            "entry":  html
        })
    else:
        return render(request, "encyclopedia/error.html", {
            "error": "Not Found",
            "message": "Requested page was not found."
        })


def search(request):
    query = request.GET.get("q")
    all_entries = util.list_entries()

    filtered = [entry for entry in all_entries if query.lower()
                in entry.lower()]
    if len(filtered) > 1:
        return render(request, "encyclopedia/search.html", {
            "query": query,
            "entries": filtered
        })
    elif len(filtered) == 1:
        entry = util.get_entry(filtered[0])
        html = markdown2.markdown(entry)
        return render(request, "encyclopedia/entry.html", {
            "title": query,
            "entry": html
        })
    else:
        return render(request, "encyclopedia/error.html", {
            "error": "Not Found",
            "message": f"No search result found for {query}."
        })


def add(request):
    class NewEntryForm(forms.Form):
        title = forms.CharField(label="Title")
        content = forms.CharField(label="Content", widget=forms.Textarea)

    if request.method == "POST":
        form = NewEntryForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            existing_entry = util.get_entry(title)
            if existing_entry:
                return render(request, "encyclopedia/add.html", {
                    "error": "Page already exists !",
                    "form": NewEntryForm()
                })
            else:
                util.save_entry(title, content)
                return HttpResponseRedirect(f"/wiki/{title}")

    return render(request, "encyclopedia/add.html", {
        "form": NewEntryForm()
    })


def edit(request, title):
    entry = util.get_entry(title)

    class EditEntryForm(forms.Form):
        content = forms.CharField(
            label="Content", widget=forms.Textarea, initial=entry)

    if request.method == "POST":
        form = EditEntryForm(request.POST)
        if form.is_valid():
            content = form.cleaned_data["content"]
            util.save_entry(title, content)
            return HttpResponseRedirect(f"/wiki/{title}")

    else:
        if entry:
            return render(request, "encyclopedia/edit.html", {
                "title": title,
                "content": entry,
                "form": EditEntryForm()
            })
        else:
            return render(request, "encyclopedia/error.html", {
                "error": "Not Found",
                "message": f"Page not Found"
            })


def random_page(request):
    entries = util.list_entries()
    random_entry = random.choice(entries)
    return HttpResponseRedirect(f"/wiki/{random_entry}")
