# AWS / CloudFormation — 12-Factor Idioms

## Config (III) — Parameter Store and Secrets Manager

```yaml
# GOOD — SSM Parameter Store for config
Parameters:
  DatabaseUrl:
    Type: AWS::SSM::Parameter::Value<String>
    Default: /app/prod/database-url

  JwtSecret:
    Type: AWS::SSM::Parameter::Value<SecureString>
    Default: /app/prod/jwt-secret

# GOOD — ECS task reading from Secrets Manager
ContainerDefinitions:
  - Name: app
    Secrets:
      - Name: DATABASE_URL
        ValueFrom: arn:aws:secretsmanager:us-east-1:123:secret:app/prod/db-url
      - Name: JWT_SECRET
        ValueFrom: arn:aws:secretsmanager:us-east-1:123:secret:app/prod/jwt
    Environment:
      - Name: PORT
        Value: "8080"
      - Name: LOG_LEVEL
        Value: "info"

# BAD — hardcoded in template
Environment:
  - Name: DATABASE_URL
    Value: postgres://prod-db:5432/app
```

## Build/Release/Run (V) — immutable ECS releases

```yaml
# GOOD — task definition references immutable image tag
ContainerDefinitions:
  - Name: app
    Image: !Sub "123456789.dkr.ecr.us-east-1.amazonaws.com/app:${ImageTag}"

Parameters:
  ImageTag:
    Type: String
    Description: Docker image tag (git SHA)
```

## Concurrency (VIII) — separate ECS services

```yaml
# GOOD — web and worker as separate ECS services
WebService:
  Type: AWS::ECS::Service
  Properties:
    TaskDefinition: !Ref WebTaskDefinition
    DesiredCount: 3

WorkerService:
  Type: AWS::ECS::Service
  Properties:
    TaskDefinition: !Ref WorkerTaskDefinition
    DesiredCount: 5     # scales independently
```

## Disposability (IX) — ECS stop timeout

```yaml
# GOOD — give app time to drain
TaskDefinition:
  Type: AWS::ECS::TaskDefinition
  Properties:
    StopTimeout: 30     # seconds before SIGKILL after SIGTERM
```

## Logs (XI) — CloudWatch

```yaml
# GOOD — stdout forwarded to CloudWatch
LogConfiguration:
  LogDriver: awslogs
  Options:
    awslogs-group: !Ref AppLogGroup
    awslogs-region: !Ref AWS::Region
    awslogs-stream-prefix: app

AppLogGroup:
  Type: AWS::Logs::LogGroup
  Properties:
    LogGroupName: /app/production
    RetentionInDays: 30
```

## Admin Processes (XII) — ECS Run Task / Lambda

```yaml
# GOOD — migration as ECS Run Task in CI
# aws ecs run-task \
#   --cluster prod \
#   --task-definition app-migrate:latest \
#   --launch-type FARGATE \
#   --network-configuration ...

# GOOD — scheduled task via EventBridge + Lambda
ScheduledRule:
  Type: AWS::Events::Rule
  Properties:
    ScheduleExpression: cron(0 3 * * ? *)
    Targets:
      - Arn: !GetAtt CleanupFunction.Arn
        Id: NightlyCleanup

CleanupFunction:
  Type: AWS::Lambda::Function
  Properties:
    Handler: index.handler
    Environment:
      Variables:
        DATABASE_URL: !Sub "{{resolve:ssm:/app/prod/database-url}}"
```
