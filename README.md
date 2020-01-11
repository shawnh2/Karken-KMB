# Karken-KMB
A Keras Model Builder software based on Keras functional API. Build your model easily and convenient to generate Python code.

## Menu
- Running
- Usage
- Future
- About

### Running
Download source code, execute `install.sh` to install environment or packages. Then run `python demo.py`.

### Usage
##### basic
1. Click node on Node Menu(left), then click on Node Scene(central), a node will be created with its arguments on Node Args(right).
2. Using Direct edge on Toolbar(top) to connect those nodes, a green dot tells its output.
3. Nodes in 'Common' and 'Utils' tab are allow to use Curves edge instead of Direct edge.
4. Once one node's arg has been referenced, it cannot be edited anymore, unless you delete it.
5. After building your own model, press Export tool button to export python code.
##### args
Every arg cell has its expect datatype, and enable auto-correct.
```
[example 1] 64:3 -> (64, 64, 64)
[example 2] dense !1 -> dense_1
```
##### search bar
You can create node through search bar with few grammars, like:
```
dense:3;units=64;traniable=False
```
then will create three dense node with its args `units=64` and `traniable=False` .
#### sidebar
It will show up only your cursor reach to the bottom area of the view.

### Future
- Application Layer
- Custom Layer
- Nodes or Arguments Prediction
- Shape Preview
- Block Type Edge

### About
1. Welcome to contribute.
2. Thanks my roommate for illustration.
3. Post on Issues if you got any.