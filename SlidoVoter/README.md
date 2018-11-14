# SlidoVoter

Utility to automate voting on [Sli.do](https://sli.do), written in python, using requests.

Install requests `pip install requests`, then run `python ./voter.py` to display help.

If you encounter error suggesting that remote API version may have changed:

1. Open browser & fire up the developer console
2. Go to sli.do event and vote some question up
3. Inspect XHR requests in the console and check what version of /api/vX.Y/events/XXX is being referenced. 

Instead of *vX.Y* you should see a number like *v0.5* or *v0.6* - that is the API version that is currently used by slido. Update it in `voter.py`, in the `apiVersion` variable. If that happens and you feel like it, you can then submit a **pull request** to this repository and I will merge your changes to make it work again. 

If you mention this utility anywhere, feel free to let me know in this repository's issues and I will put a link to your mention bellow.

## Utility mentions

- [medium.com]()
- [danieldusek.com](https://danieldusek.com/blog/4/sli-do-and-the-rigged-company-vote)