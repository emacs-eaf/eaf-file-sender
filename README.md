# EAF File Sender
This repository provides the EAF File Sender application for the [Emacs Application Framework](https://github.com/emacs-eaf/emacs-application-framework).

### Load application

```Elisp
(add-to-list 'load-path "~/.emacs.d/site-lisp/eaf-file-sender/")
(require 'eaf-file-sender)
```

### Dependency List

| Package        | Description          |
| :--------      | :------              |
| python-qrcode                  | Render QR code pointing to local files                             |
