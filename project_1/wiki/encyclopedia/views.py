from django.shortcuts import render, redirect
from random import choice
from markdown2 import Markdown
from . import util
# import bleach


def convert(title):

    content = util.get_entry(title)
    markdowner = Markdown()
    if content == None:
        return None
    else:
        return markdowner.convert(content)


def index(request):

    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def data(request, title):

    content = util.get_entry(title)

    if title.lower() in [entry.lower() for entry in util.list_entries()]:
        return render(request, "encyclopedia/data.html",{
            "title": title ,
            "content": convert(title)
        })
    else:
        return render(request, "encyclopedia/data.html",{
            "error": title ,
            "content": 1
        })


def create(request,edit):

    if request.method == "POST":
        title = request.POST.get("title")
        content = request.POST.get("content").replace('\r\n','\n')

        if title.lower() in [entry.lower() for entry in util.list_entries()]:
            if edit == "1":
                util.save_entry(title, content)
                return redirect("data", title=title)
            else:
                return render(request, "encyclopedia/data.html",{
                    "error": title ,
                    "content": 2
                })
        else:
            util.save_entry(title, content)
            return render(request, "encyclopedia/data.html",{
                "title": title ,
                "content": convert(title)
            })

    else:
        return render(request, "encyclopedia/create.html")


def random(request):
    entry = choice(util.list_entries())
    return redirect("data", entry)


def search(request):
    
    if request.method == "GET":

        quest = request.GET.get("q")
        list = util.list_entries()
        results = []

        if quest == None:
            return redirect("index")
        
        elif quest.lower() in [entry.lower() for entry in util.list_entries()]:
            return redirect("data", quest)

        else:
            for word in list:
                if quest.lower() in word.lower():
                    results.append(word)

            return render(request, "encyclopedia/search.html",{
                "results": results ,
                "quest": quest
            })


def edit(request, title=None):
    if request.method == "POST":
        title = request.POST.get("title")
        content = request.POST.get("content").replace('\r\n','\n')
        util.save_entry(title, content)
        return redirect("data", title)

    return render(request, "encyclopedia/create.html", {
        "title": title,
        "content": util.get_entry(title),
        "edit": 1
    })


def delete(request, title=None):
    
    util.remove_entry(title)
    return redirect("index")