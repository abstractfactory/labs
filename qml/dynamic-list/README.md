### Dynamic List

![][image]

In this example, a Button from QML triggers a Javascript function, from a separate `.js` file, to append a new item to a list.

```js
function createSpriteObjects() {
    console.log("Appending:", libraryModel.count);
    libraryModel.append({"name": "Item " + libraryModel.count});
}
```

[image]: https://cloud.githubusercontent.com/assets/2152766/4872924/6ba6798e-61f8-11e4-891f-493ec658d74b.png