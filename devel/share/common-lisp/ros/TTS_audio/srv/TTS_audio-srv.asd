
(cl:in-package :asdf)

(defsystem "TTS_audio-srv"
  :depends-on (:roslisp-msg-protocol :roslisp-utils )
  :components ((:file "_package")
    (:file "TTS" :depends-on ("_package_TTS"))
    (:file "_package_TTS" :depends-on ("_package"))
  ))