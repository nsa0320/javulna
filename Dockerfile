FROM eclipse-temurin:17-jre-focal

RUN useradd -ms /bin/bash webgoat
RUN chgrp -R 0 /home/webgoat
RUN chmod -R g=u /home/webgoat

USER webgoat

COPY --chown=webgoat target/webgoat-*.jar /home/webgoat/webgoat.jar

EXPOSE 8080
WORKDIR /home/webgoat

ENTRYPOINT ["java", "-jar", "/home/webgoat/webgoat.jar"]
