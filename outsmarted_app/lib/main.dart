import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import 'dart:async';
import 'package:camera/camera.dart';
import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart';

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
  MyAppState createState() => MyAppState();
}

class MyAppState extends State<MyApp> with WidgetsBindingObserver {
  late CameraController _controller;
  late Future<void> _initializeControllerFuture;
  var _game = 0;

  @override
  void initState() {
    super.initState();
    _controller = CameraController(
      widget.camera,
      ResolutionPreset.high,
    );
    _initializeControllerFuture = _controller.initialize();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    if (state == AppLifecycleState.resumed) {
      _initializeControllerFuture = _controller.initialize();
    }
  }

  void _changeGame() {
    setState(() {
      _game = _game == 0 ? 1 : 0;
    });
  }

  @override
  Widget build(BuildContext context) {
    var size = MediaQuery.of(context).size.width * 0.8;

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
        _changeGame();
        try {
          await _initializeControllerFuture;
          final image = await _controller.takePicture();
          var request = http.MultipartRequest(
              "POST", Uri.parse("http://192.168.1.2:5000/"));
          request.files.add(await http.MultipartFile.fromPath(
              "image", image.path,
              contentType: MediaType("image", "jpeg")));
          var response = await request.send();
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
      },
      child: FutureBuilder<void>(
        future: _initializeControllerFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.done) {
            return Center(
                child: Container(
                    width: size,
                    height: size,
                    decoration: BoxDecoration(
                      boxShadow: [
                        BoxShadow(
                          color: Colors.grey.withOpacity(0.5),
                          spreadRadius: 5,
                          blurRadius: 7,
                          offset:
                              const Offset(0, 2), // changes position of shadow
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
                    )));
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
              child: Text(
                _game == 0 ? 'No Game detected.' : 'TIC-TAC-TOE',
                style: const TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                  color: Color.fromARGB(255, 96, 102, 116),
                ),
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
