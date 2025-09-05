import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ModelPopupComponent } from './model-popup.component';

describe('ModelPopupComponentComponent', () => {
  let component: ModelPopupComponent;
  let fixture: ComponentFixture<ModelPopupComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [ModelPopupComponent]
    });
    fixture = TestBed.createComponent(ModelPopupComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
