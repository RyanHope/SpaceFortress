;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;; Helper functions
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(defmacro defp (&rest body)
  `(p-fct ',body))

(defmacro defp* (&rest body)
  `(p*-fct ',body))

(defun run-until-break (&key (real-time nil))
  (run-until-condition (lambda () nil) :real-time real-time))

(defun degrees (x) (* x (/ 180 pi)))

(defun to-target-orientation(selfx selfy targx targy)
  (round (mod (- (degrees (atan (- targx selfx) (- selfy targy))) 90) 360)))

(defun point-on-line (px py x1 y1 x2 y2)
  (= (- py y1) (* (/ (- y2 y1) (- x2 x1)) (- px x1))))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;; Model initialization
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(clear-all)

(define-model spacefortress)

(jni-register-event-hook :break (lambda () (schedule-break-after-all)))

(sgp :jni-hostname "127.0.0.1" :jni-port 5555 :jni-sync t)

(sgp :needs-mouse nil
     :v t
     :esc t
     :er t
     :ul t
     :ppm 1
     :mas 1
     :mp 1
     :randomize-time nil
     :dual-execution-stages t
     )

;;; Goals
(chunk-type study-mine-letters state)
(chunk-type monitor)
(chunk-type shoot-fortress subgoal)
(chunk-type shoot-mine subgoal)
(chunk-type avoid-shells subgoal)
(chunk-type avoid-fortress subgoal)
(chunk-type avoid-warping subgoal)
(chunk-type avoid-mine subgoal)

;;; New chunk types
(chunk-type game-settings mines)
(chunk-type (token-location (:include visual-location)) orientation velocity)
(chunk-type (token-object (:include visual-object)) orientation velocity)
(chunk-type (ship (:include token-object)))
(chunk-type (fortress (:include token-object)))
(chunk-type (mine (:include token-object)))
(chunk-type (shell (:include token-object)))
(chunk-type (missile (:include token-object)))
(chunk-type (rect-location (:include visual-location)) top bottom left right)
(chunk-type (rect-object (:include visual-object)) top bottom left right)
(chunk-type (world-border (:include rect-object)))

(chunk-type mine-letters letter1 letter2 letter3)

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;; Productions
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(defp **start**
  ?goal> buffer empty
  ?retrieval> buffer empty state free
  ?manual> processor free
  ?manual-right> pinkie free pinkie up
  ==>
  +retrieval> isa game-settings
  +manual> isa delayed-punch hand right finger pinkie
  )

(defp **prep-new-game**
  ?goal> buffer empty
  retrieval> isa game-settings
  ==>
  +goal> retrieval
  )

(defp **new-game**
  ?goal> buffer empty
  ?retrieval> buffer empty state free
  ?manual> processor free
  ?manual-right> pinkie free pinkie up
  ==>
  +retrieval> isa game-settings
  +manual> isa delayed-punch hand right finger pinkie
  )
