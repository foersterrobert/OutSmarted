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

// A screen that allows users to take a picture using a given camera.
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
  late CameraController _controller;
  late Future<void> _initializeControllerFuture;
  final double _maxZoom = 8.0;
  final double _minZoom = 1.0;
  double _zoom = 1.0;
  var _game = 0;

  @override
  void initState() {
    super.initState();
    _controller = CameraController(
      widget.camera,
      ResolutionPreset.high,
    );
    _initializeControllerFuture = _controller.initialize();
    // _maxZoom = _controller.getMaxZoomLevel();
    // _minZoom = _controller.getMinZoomLevel();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _handleTap() async {
    try {
      await _initializeControllerFuture;
      final image = await _controller.takePicture();
      final img_lib.Image? capturedImage =
          img_lib.decodeImage(await File(image.path).readAsBytes());
      final img_lib.Image orientedImage = img_lib.bakeOrientation(capturedImage!);
      await File(image.path).writeAsBytes(img_lib.encodeJpg(orientedImage));
      var request =
          http.MultipartRequest("POST", Uri.parse("http://robertfoerster.pythonanywhere.com/")); // http://192.168.1.2:5000/
      request.files.add(await http.MultipartFile.fromPath("image", image.path,
          contentType: MediaType("image", "jpeg")));
      request.fields['game'] = _game.toString();
      var streamedResponse = await request.send();
      var response = await http.Response.fromStream(streamedResponse);
      final responseJson = jsonDecode(response.body);
      setState(() {
        _game = responseJson['game'];
      });
      showDialog(
          context: context,
          builder: (BuildContext context) {
            return AlertDialog(
              title: const Text('Result'),
              content: Text(responseJson['state'].toString()),
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

    Widget cameraPreview = GestureDetector(
      onTap: () async {
        _handleTap();
      },
      child: FutureBuilder<void>(
        future: _initializeControllerFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.done) {
            return Container(
                padding: EdgeInsets.only(left: screenSize * 0.1),
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
                                        Opacity(
                                          opacity: 0.8,
                                          child: Image.asset(
                                            'assets/images/tictactoe/tictactoeGrid.png',
                                            width: size,
                                            height: size *
                                                _controller.value.aspectRatio,
                                          ),
                                        )
                                    ],
                                  ),
                                ),
                              ),
                            ),
                          ),
                        )),
                    SizedBox(
                      height: size,
                      width: screenSize * 0.1,
                      child: RotatedBox(
                        quarterTurns: 3,
                        child: Slider(
                          value: _zoom,
                          activeColor: const Color.fromARGB(255, 143, 155, 155),
                          inactiveColor: const Color.fromARGB(255, 191, 199, 204),
                          thumbColor: const Color.fromARGB(255, 150, 192, 211),
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
                    )
                  ],
                ));
          } else {
            return const Center(child: CircularProgressIndicator());
          }
        },
      ),
    );

    Widget gameVis = Center(
      child: Container(
        margin: const EdgeInsets.fromLTRB(0, 8, 0, 0),
        child: Image.asset(
          'assets/images/tictactoe/tictactoeFull.png',
          width: size,
          height: size,
        ),
      ),
    );

    return Scaffold(
      body: ListView(
        children: [
          header,
          cameraPreview,
          Center(
            child: Container(
              margin: const EdgeInsets.fromLTRB(0, 8, 0, 0),
              width: size,
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    _game == 0 ? 'No Game detected.' : 'TIC-TAC-TOE',
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
                            });
                          },
                        )
                      : Container(),
                ],
                
              ),
            ),
          ),
          gameVis,
          footer,
        ],
      ),
    );
  }
}
