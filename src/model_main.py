import model_server

if __name__ == '__main__':
    s = model_server.Server(model_server.Logger())
    s.handle_connections()
