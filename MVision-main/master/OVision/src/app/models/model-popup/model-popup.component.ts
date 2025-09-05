import { Component, EventEmitter, Output, Input } from '@angular/core';

@Component({
  selector: 'app-model-popup',
  templateUrl: './model-popup.component.html',
  styleUrls: ['./model-popup.component.sass']
})
export class ModelPopupComponent {
  @Input() modelClasses: string[] = ['test'];
  @Output() close = new EventEmitter<void>();

  closePopup() {
    this.close.emit();
  }
}
