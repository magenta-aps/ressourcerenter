## URL Patterns

Url patterns should be based on which model they refer to, e.g.:
* `path('some_model/'...`                      For listing items of a given model, with url parameters specifying how to filter, or for creating a new item
* `path('some_model/<int:pk>/'...`             For reading or changing a specific item.
                                               The HTTP method should then be used to specify the operation (read, write, delete etc.)
* `path('some_model/<int:pk>/some_aspect'...`  For reading or changing a certail aspect of an item, such as obtaining specialized data that is not included normally

this is basically REST applied to our url patterns

If a button should perform an action (not just navigating to a page), 
it should be wrapped in a form that uses POST, *not* merely be a link
to an endpoint that answers and executes on a GET request

A search interface should receive all parameters as URL parameters, not having any
parameters as part of the path. This includes hardcoded searches in links.
