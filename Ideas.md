[Enhancements requests from the issue tracker](http://code.google.com/p/labyrinth/issues/list?can=2&q=type:Enhancement)

Tell us your ideas about labyrinth and we will add them here or add them yourself.

  * Speech bubble
> > Show extended info as a speech bubble that can be opened and closed.
  * Fly by presentation
> > Start a presentation by zooming out and show the complete mindmap. Select a thought zoom in smoothly and show the extended content beside the thought if the user is near enough the thought. After selecting the thought again zoom out again smoothly to see the complete map.
  * Tomboy Applet Style
> > Add Labyrinth to the applet panel and manage maps like Tomboy does with notes. See [Issue 77](https://code.google.com/p/labyrinth/issues/detail?id=77) for some mockups provided by frandavid100.
  * Gnome integration
> > Theme, Drag and Drop, ...
  * Grouping of thoughts into "meta-thoughts". This would basically colour a region behind the thoughts to it was clear the thoughts are in related areas.  Moving the big coloured area would move all associated thoughts.  Moving a single thought in the backgrounded area would only move that thought.

  * A11y.  My initial idea was to make thoughts visible to a11y tools. But this is (very) difficult and doesn't really aid in a11y for some circumstances.  To compliment this / replace this, I thought about having a treeview of thoughts, with the children being sub-members. This would get us free a11y through the GTK treeview implementation and still preserves some of the information in the map.  Thoughts which are children of multiple nodes could be italicised or marked in some way. It's not a great solution, but what I came up with. ([Issue 97](https://code.google.com/p/labyrinth/issues/detail?id=97))

  * Exporting.  For images, exporting of extended buffers is never going to happen.  However, for pdf / ps / printing, it'd be nice to have an option to include the extended buffers somehow.  I'm not sure of the mechanism for doing this.  Maybe have each thought with an extended buffer assigned a small number, which is put in the top right, followed by the extended thought below, with the relevant number.  This doesn't sound clear at all.  I'll do a mock up at some point.

  * Speed.  I know Matthias has implemented some speedups, but there are more available.  The biggest problem is when moving the canvas around, as all thoughts visible must be redrawn every movement.  Maybe we could get around this be keeping a cache of the current view and blatting [1](1.md) that at the correct offset and only redrawing everything once movement has stopped.

  * Speed (2).  Another slow-down is moving thoughts around.  One solution to this is to track which thought caused the redraw and pass this to every link we request drawing.  The link would then know if it's associated with that thought and draw itself.  Maybe it'd be enough to only draw the thought and all links.  There's also an issue here with dragging thoughts over other thoughts.  Guess we'd need to keep the original and new coords and redraw that area.

  * More keyboard navigation possibilities.

  * HIG compliance ([Issue 76](https://code.google.com/p/labyrinth/issues/detail?id=76))

  * Import from (at least) kdissert and freemind

  * Printing support for maps

  * Hide / show thoughts

  * Popup menus everywhere

  * Allow to align links and thoughts ([Issue 71](https://code.google.com/p/labyrinth/issues/detail?id=71), [Issue 87](https://code.google.com/p/labyrinth/issues/detail?id=87))

  * ~~Bezier curves~~

## Links ##
  * Abbility to add text

## Image Thoughts ##
  * ~~Abbility to change images~~

## Drawing Thoughts ##
  * Different pen widths