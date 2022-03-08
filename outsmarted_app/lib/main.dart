import 'dart:async';
import 'package:camera/camera.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();

  final cameras = await availableCameras();
  final firstCamera = cameras.first;

  runApp(MyApp(camera: firstCamera));
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

class MyAppState extends State<MyApp> {
  late CameraController _controller;
  late Future<void> _initializeControllerFuture;

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
  Widget build(BuildContext context) {
    Widget cameraPreview = Container(
        child: GestureDetector(
            onTap: () async {
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
                print('test :)');
              }
            },
            child: FutureBuilder<void>(
              future: _initializeControllerFuture,
              builder: (context, snapshot) {
                if (snapshot.connectionState == ConnectionState.done) {
                  var size = MediaQuery.of(context).size.width;
                  return Container(
                    width: size,
                    height: size,
                    padding: EdgeInsets.all(32.0),
                    child: ClipRect(
                      child: OverflowBox(
                        alignment: Alignment.center,
                        child: FittedBox(
                          fit: BoxFit.fitWidth,
                          child: Container(
                            width: size,
                            height: size * _controller.value.aspectRatio,
                            child: CameraPreview(_controller),
                          ),
                        ),
                      ),
                    ),
                  );
                } else {
                  return const Center(child: CircularProgressIndicator());
                }
              },
            )
          )
        );

    return MaterialApp(
      title: 'OutSmarted',
      home: Scaffold(
        appBar: AppBar(title: const Text('OutSmarted')),
        body: Column(
          children: [
            cameraPreview,
            const Text('OutSmarted', textAlign: TextAlign.center,),
          ],
        ),
      )
    );
  }
}
