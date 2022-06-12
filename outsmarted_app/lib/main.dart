import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import 'dart:async';
import 'package:camera/camera.dart';
import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart';
import 'package:image/image.dart' as img_lib;

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();

  final cameras = await availableCameras();
  final firstCamera = cameras.first;

  runApp(
    MediaQuery(
      data: const MediaQueryData(),
      child: MaterialApp(
        title: 'OutSmarted',
        theme: ThemeData(
          scaffoldBackgroundColor: const Color.fromARGB(233, 233, 242, 255),
        ),
        home: MyApp(
          camera: firstCamera,
        ),
        debugShowCheckedModeBanner: false,
      ),
    ),
  );
}

class MyApp extends StatefulWidget {
  const MyApp({
    Key? key,
    required this.camera,
  }) : super(key: key);

  final CameraDescription camera;

  @override
  State<MyApp> createState() => _MyAppState();
}

class _MyAppState extends State<MyApp> {
  final serverEndpoint = 'http://192.168.1.7:5000';
  late CameraController _controller;
  late Future<void> _initializeControllerFuture;
  bool _isLoading = false;
  final double _maxZoom = 8.0;
  final double _minZoom = 1.0;
  double _zoom = 1.0;
  var _game = 0;
  var _player = 0;
  final _infoMap = {
    '0': ['Player 1', '', 'Player 2', 'No Game detected.'],
    '1': ['❌', '', '⭕', 'TIC-TAC-TOE'],
    '2': ['🔴', '', '🟡', 'CONNECT-4'],
  };
  List<dynamic> _state = [];

  @override
  void initState() {
    super.initState();
    _controller = CameraController(
      widget.camera,
      ResolutionPreset.high,
    );
    _initializeControllerFuture = _controller.initialize();
    _controller.setFlashMode(FlashMode.off);
    // _maxZoom = _controller.getMaxZoomLevel();
    // _minZoom = _controller.getMinZoomLevel();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _handleTap() async {
    setState(() {
      _isLoading = true;
    });
    try {
      await _initializeControllerFuture;
      final image = await _controller.takePicture();
      final img_lib.Image? capturedImage =
          img_lib.decodeImage(await File(image.path).readAsBytes());
      final img_lib.Image orientedImage =
          img_lib.bakeOrientation(capturedImage!);
      await File(image.path).writeAsBytes(img_lib.encodeJpg(orientedImage));
      if (_game == 0) {
        var request = http.MultipartRequest(
            "POST", Uri.parse("$serverEndpoint/game"));
        request.files.add(await http.MultipartFile.fromPath("image", image.path,
            contentType: MediaType("image", "jpeg")));
        var streamedResponse = await request.send();
        var response = await http.Response.fromStream(streamedResponse);
        final responseJson = jsonDecode(response.body);
        if (responseJson['game'] == 1) {
          setState(() {
            _game = 1;
            _player = 1;
            _state = [
              [0, 0, 0],
              [0, 0, 0],
              [0, 0, 0]
            ];
          });
          showDialog(
              context: context,
              builder: (BuildContext context) {
                return AlertDialog(
                  title: const Text('Tic-Tac-Toe detected'),
                  content: Text(
                    'Tic-Tac-Toe: ${responseJson['out'].elementAt(0).toString()}\nConnect-4: ${responseJson['out'].elementAt(1).toString()}'
                  ),
                  actions: <Widget>[
                    TextButton(
                      child: const Text(
                        'Player1 ⭕',
                        style: TextStyle(
                          fontSize: 18,
                          color: Color.fromARGB(255, 96, 102, 116),
                        ),
                      ),
                      onPressed: () {
                        setState(() {
                          _player = 1;
                        });
                        Navigator.of(context).pop();
                      },
                    ),
                    TextButton(
                      child: const Text(
                        'Player2 ❌',
                        style: TextStyle(
                          fontSize: 18,
                          color: Color.fromARGB(255, 96, 102, 116),
                        ),
                      ),
                      onPressed: () {
                        setState(() {
                          _player = -1;
                        });
                        Navigator.of(context).pop();
                      },
                    ),
                  ],
                );
              });
        } else {
          setState(() {
            _game = 2;
            _player = 1;
            _state = [
              [0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0],
            ];
          });
          showDialog(
              context: context,
              builder: (BuildContext context) {
                return AlertDialog(
                  title: const Text('Connect-4 detected'),
                  content: Text(
                    'Tic-Tac-Toe: ${responseJson['out'].elementAt(0).toString()}\nConnect-4: ${responseJson['out'].elementAt(1).toString()}'
                  ),
                  actions: <Widget>[
                    TextButton(
                      child: const Text(
                        'Player1 🟡',
                        style: TextStyle(
                          fontSize: 18,
                          color: Color.fromARGB(255, 96, 102, 116),
                        ),
                      ),
                      onPressed: () {
                        setState(() {
                          _player = 1;
                        });
                        Navigator.of(context).pop();
                      },
                    ),
                    TextButton(
                      child: const Text(
                        'Player2 🔴',
                        style: TextStyle(
                          fontSize: 18,
                          color: Color.fromARGB(255, 96, 102, 116),
                        ),
                      ),
                      onPressed: () {
                        setState(() {
                          _player = -1;
                        });
                        Navigator.of(context).pop();
                      },
                    ),
                  ],
                );
              });
        }
      } else {
        var request = http.MultipartRequest(
            "POST", Uri.parse("$serverEndpoint/state"));
        request.files.add(await http.MultipartFile.fromPath("image", image.path,
            contentType: MediaType("image", "jpeg")));
        request.fields['game'] = _game.toString();
        request.fields['player'] = _player.toString();
        var streamedResponse = await request.send();
        var response = await http.Response.fromStream(streamedResponse);
        final responseJson = jsonDecode(response.body);
        final _bytesImage = base64Decode(responseJson['image'].toString());

        setState(() {
          _state = responseJson['state'];
        });

        showDialog(
            context: context,
            builder: (BuildContext context) {
              return AlertDialog(
                title: const Text('State detected'),
                content: Image.memory(
                  _bytesImage,
                  fit: BoxFit.cover,
                ),
                actions: <Widget>[
                  TextButton(
                    child: const Text('OK'),
                    onPressed: () {
                      Navigator.of(context).pop();
                    },
                  ),
                ],
              );
            });
      }
    } catch (e) {
      showDialog(
          context: context,
          builder: (BuildContext context) {
            return AlertDialog(
              title: const Text('Error'),
              content: const Text("Couldn't connect to server! 😬"),
              actions: <Widget>[
                TextButton(
                  child: const Text('OK'),
                  onPressed: () {
                    Navigator.of(context).pop();
                  },
                ),
              ],
            );
          });
    }
    setState(() {
      _isLoading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    var screenSize = MediaQuery.of(context).size.width;
    var size = screenSize * 0.8;

    Widget header = Center(
      child: Container(
        margin: const EdgeInsets.fromLTRB(0, 4, 0, 2),
        width: size,
        child: const Text(
          '🧠 OutSmarted.',
          style: TextStyle(
            fontSize: 26,
            fontWeight: FontWeight.bold,
            color: Colors.black,
          ),
        ),
      ),
    );

    Widget footer = Center(
      child: Container(
        margin: const EdgeInsets.fromLTRB(0, 12, 0, 6),
        child: InkWell(
          child: const Text(
            '👾 GitHub',
            style: TextStyle(
              fontSize: 14,
              color: Color.fromARGB(255, 96, 102, 116),
            ),
          ),
          onTap: () => launch('https://github.com/foersterrobert/OutSmarted'),
        ),
      ),
    );

    Widget cameraSlider = SizedBox(
      height: size,
      width: screenSize * 0.1,
      child: RotatedBox(
        quarterTurns: 3,
        child: Slider(
          value: _zoom,
          activeColor: const Color.fromARGB(255, 143, 155, 155),
          inactiveColor: const Color.fromARGB(255, 191, 199, 204),
          thumbColor: const Color.fromARGB(255, 161, 201, 202),
          onChanged: (value) {
            setState(() {
              _zoom = value;
              _controller.setZoomLevel(_zoom);
            });
          },
          min: _minZoom.toDouble(),
          max: _maxZoom.toDouble(),
          divisions: _maxZoom.toInt() * 2,
        ),
      ),
    );

    Widget cameraPreview = GestureDetector(
      onTap: () async {
        if (_isLoading == false) {
          _handleTap();
        }
      },
      child: FutureBuilder<void>(
        future: _initializeControllerFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.done) {
            return Container(
                margin: EdgeInsets.only(left: screenSize * 0.1),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Container(
                        width: size,
                        height: size,
                        decoration: BoxDecoration(
                          boxShadow: [
                            BoxShadow(
                              color: Colors.grey.withOpacity(0.5),
                              spreadRadius: 5,
                              blurRadius: 7,
                              offset: const Offset(
                                  0, 2), // changes position of shadow
                            ),
                          ],
                        ),
                        child: ClipRRect(
                          borderRadius: BorderRadius.circular(4),
                          child: ClipRect(
                            child: OverflowBox(
                              alignment: Alignment.center,
                              child: FittedBox(
                                fit: BoxFit.fitWidth,
                                child: SizedBox(
                                  width: size,
                                  height: size * _controller.value.aspectRatio,
                                  child: Stack(
                                    children: <Widget>[
                                      CameraPreview(_controller),
                                      if (_game == 1)
                                        Image.asset(
                                          'assets/images/tictactoeGrid.png',
                                          width: size,
                                          height: size *
                                              _controller.value.aspectRatio,
                                        ),
                                      if (_game == 2)
                                        Image.asset(
                                          'assets/images/connectfourGrid.png',
                                          width: size,
                                          height: size *
                                              _controller.value.aspectRatio,
                                        ),
                                    ],
                                  ),
                                ),
                              ),
                            ),
                          ),
                        )),
                    cameraSlider,
                  ],
                ));
          } else {
            return const Center(child: CircularProgressIndicator());
          }
        },
      ),
    );

    Widget progressBar = Center(
      child: Container(
          margin: const EdgeInsets.fromLTRB(0, 2, 0, 0),
          width: size,
          child: ClipRRect(
            child: const LinearProgressIndicator(
              backgroundColor: Color.fromARGB(255, 143, 155, 155),
              color: Color.fromARGB(255, 161, 201, 202),
            ),
            borderRadius: BorderRadius.circular(4),
          )),
    );

    Widget gameInfo = Center(
      child: Container(
        margin: const EdgeInsets.fromLTRB(0, 6, 0, 0),
        width: size,
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              '${_infoMap[_game.toString()]?.elementAt(3)} ${_infoMap[_game.toString()]?.elementAt(_player + 1)}',
              style: const TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
                color: Color.fromARGB(255, 96, 102, 116),
              ),
            ),
            _game != 0
                ? IconButton(
                    padding: EdgeInsets.zero,
                    constraints: const BoxConstraints(),
                    icon: const Icon(
                      Icons.exit_to_app,
                      color: Color.fromARGB(255, 96, 102, 116),
                    ),
                    onPressed: () {
                      setState(() {
                        _game = 0;
                        _player = 0;
                        _state = [];
                      });
                    },
                  )
                : IconButton(
                    padding: EdgeInsets.zero,
                    constraints: const BoxConstraints(),
                    icon: const Icon(
                      Icons.search,
                      color: Color.fromARGB(255, 96, 102, 116),
                    ),
                    onPressed: () {
                      showDialog(
                          context: context,
                          builder: (BuildContext context) {
                            return AlertDialog(
                              title: const Text('Select a game'),
                              actions: <Widget>[
                                TextButton(
                                  child: const Text('Tic-Tac-Toe'),
                                  onPressed: () {
                                    setState(() {
                                      _game = 1;
                                      _player = 1;
                                      _state = [
                                        [0, 0, 0],
                                        [0, 0, 0],
                                        [0, 0, 0]
                                      ];
                                    });
                                    Navigator.of(context).pop();
                                    showDialog(
                                        context: context,
                                        builder: (BuildContext context) {
                                          return AlertDialog(
                                            title: const Text(
                                                'Tic-Tac-Toe selected'),
                                            actions: <Widget>[
                                              TextButton(
                                                child: const Text(
                                                  'Player1 ⭕',
                                                  style: TextStyle(
                                                    fontSize: 18,
                                                    color: Color.fromARGB(
                                                        255, 96, 102, 116),
                                                  ),
                                                ),
                                                onPressed: () {
                                                  setState(() {
                                                    _player = 1;
                                                  });
                                                  Navigator.of(context).pop();
                                                },
                                              ),
                                              TextButton(
                                                child: const Text(
                                                  'Player2 ❌',
                                                  style: TextStyle(
                                                    fontSize: 18,
                                                    color: Color.fromARGB(
                                                        255, 96, 102, 116),
                                                  ),
                                                ),
                                                onPressed: () {
                                                  setState(() {
                                                    _player = -1;
                                                  });
                                                  Navigator.of(context).pop();
                                                },
                                              ),
                                            ],
                                          );
                                        });
                                  },
                                ),
                                TextButton(
                                  child: const Text('Connect-4'),
                                  onPressed: () {
                                    setState(() {
                                      _game = 2;
                                      _player = 1;
                                      _state = [
                                        [0, 0, 0, 0, 0, 0, 0],
                                        [0, 0, 0, 0, 0, 0, 0],
                                        [0, 0, 0, 0, 0, 0, 0],
                                        [0, 0, 0, 0, 0, 0, 0],
                                        [0, 0, 0, 0, 0, 0, 0],
                                        [0, 0, 0, 0, 0, 0, 0],
                                      ];
                                    });
                                    Navigator.of(context).pop();
                                    showDialog(
                                        context: context,
                                        builder: (BuildContext context) {
                                          return AlertDialog(
                                            title: const Text(
                                                'Connect-4 selected'),
                                            actions: <Widget>[
                                              TextButton(
                                                child: const Text(
                                                  'Player1 🟡',
                                                  style: TextStyle(
                                                    fontSize: 18,
                                                    color: Color.fromARGB(
                                                        255, 96, 102, 116),
                                                  ),
                                                ),
                                                onPressed: () {
                                                  setState(() {
                                                    _player = 1;
                                                  });
                                                  Navigator.of(context).pop();
                                                },
                                              ),
                                              TextButton(
                                                child: const Text(
                                                  'Player2 🔴',
                                                  style: TextStyle(
                                                    fontSize: 18,
                                                    color: Color.fromARGB(
                                                        255, 96, 102, 116),
                                                  ),
                                                ),
                                                onPressed: () {
                                                  setState(() {
                                                    _player = -1;
                                                  });
                                                  Navigator.of(context).pop();
                                                },
                                              ),
                                            ],
                                          );
                                        });
                                  },
                                )
                              ],
                            );
                          });
                    },
                  ),
          ],
        ),
      ),
    );

    Widget tictactoeVis = Stack(children: [
      Image.asset(
        'assets/images/tictactoe.png',
        width: size,
        height: size,
      ),
      for (int i = 0; i < _state.length; i++)
        for (int j = 0; j < _state[i].length; j++)
          if (_state[i][j] != 0)
            Positioned(
                left: j * size / 3,
                top: i * size / 3,
                child: SizedBox(
                  width: size / 3,
                  height: size / 3,
                  child: Center(
                    child: Image.asset(
                      'assets/images/$_game.${_state[i][j]}.png',
                      width: size / 3.4,
                      height: size / 3.4,
                    ),
                  ),
                )),
    ]);

    Widget connectfourVis = Stack(children: [
      Image.asset(
        'assets/images/connectfour.png',
        width: size,
        height: size,
      ),
      for (int i = 0; i < _state.length; i++)
        for (int j = 0; j < _state[i].length; j++)
          if (_state[i][j] != 0)
            Positioned(
                left: j * size / (_state[0].length * 1.06) + size / 45,
                top: i * size / (_state.length * 1.33) + size / 8,
                child: SizedBox(
                  width: size / _state[0].length,
                  height: size / _state[0].length,
                  child: Center(
                    child: Image.asset(
                      'assets/images/$_game.${_state[i][j]}.png',
                      width: size / (_state[0].length * 1.28),
                      height: size / (_state[0].length * 1.28),
                    ),
                  ),
                )),
    ]);

    Widget gameVis = Center(
      child: Container(
        margin: const EdgeInsets.fromLTRB(0, 8, 0, 0),
        child: [
          Image.asset(
            'assets/images/board.png',
            width: size,
            height: size,
          ),
          tictactoeVis,
          connectfourVis,
        ].elementAt(_game),
      ),
    );

    return Scaffold(
      body: ListView(
        children: [
          header,
          cameraPreview,
          if (_isLoading) progressBar,
          gameInfo,
          gameVis,
          footer,
        ],
      ),
    );
  }
}
