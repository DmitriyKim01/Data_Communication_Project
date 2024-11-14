class Config:
  HOSTNAME = "35.183.124.89"
  PORT = 1883
  GRPC_SERVER_ADDRESS = "localhost:50051"
  SENSOR_TYPES = ['All', 'Temperature', 'Humidity', 'Wind']
  SENSOR_IDS = ['All', '0001', '0002', '0003']
  
  @staticmethod
  def display_options(options, question):
    if not options:
      raise Exception('No options provided')
    if not isinstance(options, list):
      raise Exception('Invalid options type')
    if not question:
      raise Exception('No question provided')
    if not isinstance(question, str):
      raise Exception('Invalid question type')
    
    header = 'Index | Options \n'
    message=  ''
    
    for i in range(len(options)):
      if i < 9:
        message += f' ({i + 1})  | '
      else:
        message += f' ({i + 1})  | '
      message += options[i] + '\n'
    return header + message + question
  
  @staticmethod
  def validate_options(options, question):
    if not options:
      raise Exception('No options provided')
    if not isinstance(options, list):
      raise Exception('Invalid options type')
    if not question:
      raise Exception('No question provided')
    if not isinstance(question, str):
      raise Exception('Invalid question type')
    
    attempts = 0
    user_input = input(Config.display_options(options, question))
    is_valid_choice = False
    
    while not is_valid_choice:
      if user_input.isdigit():
        index = int(user_input)
        if 1 <= index <= len(options):
            user_input = options[index - 1]
            
      if user_input in options:
        is_valid_choice = True
        return user_input
      else:
        attempts += 1
        print(f'Invalid option. Please try again. {attempts}')
        user_input = input(Config.display_options(options, question))
      
